import unicodedata
from random import shuffle

from PIL import Image
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
    if x or y or w or h:
        cropped_image = image.crop((x, y, w + x, h + y))  # left, upper, right, and lower pixel
        resized_image = cropped_image.resize((500, 500), Image.ANTIALIAS)
        resized_image.save(course.image.path)
        return True
    return False


def check_teacher_field(form, request):
    """
    Check whether only a single teacher is registered in the organization and if so, select them and make the field
    read-only so the user does not need to bother.
    """

    teacher_field = form.fields['teacher']
    teachers = User.objects.filter(organization_id=request.user.organization.id).order_by('date_created')
    teacher_field.queryset = teachers
    if teachers.count() == 1:
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
