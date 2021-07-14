import unicodedata
from collections import defaultdict
from random import shuffle

from PIL import Image
from allauth.account.adapter import get_adapter
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import mail_managers
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils.text import slugify

from catalog.models import Course
from users.models import User


# taggit
def comma_splitter(tag_string):
    return [t.strip().lower() for t in tag_string.split(',') if t.strip()]


# taggit
def comma_joiner(tags):
    return ', '.join(t.name for t in tags)


def asciify(value):
    return unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')


def get_slugs(value):
    return [slugify(t.strip()) for t in value.split(',') if t.strip()]


def is_approval_requested(cd, course, original_desc, original_name, request):
    """
    If the user changed name or description of a course, it must be re-approved by administrators.
    Set status to DRAFT and send an email notification with a link to course in admin panel.
    """

    approval_requested = False
    if (original_name != course.name or original_desc != course.description) \
            and course.status != Course.Status.DRAFT:
        course.name = cd['name'].capitalize()
        course.status = Course.Status.DRAFT
        approval_requested = True
        course_url_admin = request.build_absolute_uri(course.get_absolute_url_admin())
        mail_managers(f'Aktivita upravena - čeká na schválení', f'Název aktivity:\n{course.name}\n\n{course_url_admin}')
    return approval_requested


def post_process_image(cleaned_data, course):
    """Get coordinates from hidden fields of the form. Use them to crop an uploaded image and resize it."""

    image = Image.open(course.image)
    x, y, w, h = cleaned_data.get('x'), cleaned_data.get('y'), cleaned_data.get('width'), cleaned_data.get('height')
    if None in (x, y, w, h):
        # in case cropper.js failed, crop from upper left corner
        x, y, w, h = 0, 0, settings.SIDE_LENGTH_COURSE_IMG, settings.SIDE_LENGTH_COURSE_IMG
    cropped_image = image.crop((x, y, w + x, h + y))  # left, upper, right, and lower pixel
    resized_image = cropped_image.resize((settings.SIDE_LENGTH_COURSE_IMG, settings.SIDE_LENGTH_COURSE_IMG),
                                         Image.ANTIALIAS)
    resized_image.save(course.image.path)


def check_teacher_field(form, request):
    """
    Modify behavior of the field base on user's role and members.
    Role COORDINATOR: If there are no other members, pre-select the coordinator.
    Role TEACHER: Pre-select the current user.
    """
    teacher_field = form.fields['teacher']
    if request.user.role == User.Roles.COORDINATOR:
        qs = User.objects.filter(organization_id=request.user.organization.id).order_by('date_created')
    else:
        qs = User.objects.filter(pk=request.user.pk)
    teacher_field.queryset = qs
    if qs.count() == 1:
        # simulate readonly attribute for <select> element
        teacher_field.widget.attrs.update({'style': 'pointer-events: none; background-color: #e9ecef;',
                                           'tabindex': "-1"})


def paginate(request, objects, per_page=10):
    paginator = Paginator(objects, per_page)
    page = request.GET.get('page')
    try:
        courses = paginator.page(page)
        custom_page_range = paginator.get_elided_page_range(page, on_each_side=2, on_ends=1)
    except PageNotAnInteger:
        courses = paginator.page(1)
        custom_page_range = paginator.get_elided_page_range(1, on_each_side=2, on_ends=1)
    except EmptyPage:
        courses = paginator.page(paginator.num_pages)
        custom_page_range = paginator.get_elided_page_range(paginator.num_pages, on_each_side=2, on_ends=1)
    return courses, custom_page_range, paginator.count


def get_sponsored_courses_list(qs):
    sponsored_courses = qs.filter(is_ad=True)
    sp_courses_list = list(sponsored_courses)[:3]
    shuffle(sp_courses_list)
    return sp_courses_list


def make_week_schedule(course):
    week_schedule = defaultdict(list)
    for j in range(7, 23):  # create empty schedule
        for i in range(7):
            week_schedule[j].append(' ')
    for i in course.week_schedule.all():
        week_schedule[i.hour][i.day_of_week] = 'X'
    return dict(week_schedule)


def send_notification_course_registered(instance):
    current_site = Site.objects.get_current()
    course_name = instance.name
    get_adapter().send_mail('catalog/course/email/registered', instance.teacher.email,
                            {'course_name': course_name,
                             'current_site': current_site})
