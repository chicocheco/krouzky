from collections import defaultdict
from datetime import datetime
from random import shuffle

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage, mail_managers
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from django.utils.timezone import localtime

from users.models import User
from .filters import CourseFilter
from .forms import (UpdateOrganizationForm, RenameOrganizationForm, RegisterOrganizationForm, CourseForm,
                    OneoffCourseForm, ContactTeacherForm)
from .models import Course, Organization
from .utils import is_approval_requested, post_process_image, check_teacher_field, paginate


def home(request):
    return render(request, 'catalog/home.html')


def gdpr(request):
    return render(request, 'catalog/gdpr.html')


def conditions(request):
    return render(request, 'catalog/conditions.html')


def cooperation(request):
    return render(request, 'catalog/cooperation.html', {'section': 'cooperation'})


def about_us(request):
    return render(request, 'catalog/about.html', {'section': 'about_us'})


@login_required
def dashboard(request):
    user_organization = request.user.organization
    return render(request,
                  'catalog/dashboard.html',
                  {'user_organization': user_organization})


def search(request):
    query = None
    course_filter = CourseFilter(request.GET, Course.published.all().select_related())
    form = course_filter.form  # detach form for rendering
    if 'q' in request.GET:
        form.fields['q'].initial = request.GET.get('q')
    counter = course_filter.qs.count()
    courses, custom_page_range = paginate(request, course_filter.qs)
    # sponsored
    sponsored_courses = course_filter.qs.filter(is_ad=True)
    sp_courses_list = list(sponsored_courses)[:3]
    shuffle(sp_courses_list)
    return render(request, 'catalog/course/search.html', {'courses': courses,
                                                          'sponsored_courses': sp_courses_list,
                                                          'counter': counter,
                                                          'form': form,
                                                          'query': query,
                                                          'custom_page_range': custom_page_range,
                                                          'section': 'search'})


def course_list_by_organization(request, slug):
    organization = get_object_or_404(Organization, slug=slug)
    object_list = Course.objects.filter(organization=organization).select_related()
    counter = object_list.count()
    courses, custom_page_range = paginate(request, object_list)
    return render(request, 'catalog/course/list_organization.html', {'courses': courses,
                                                                     'counter': counter,
                                                                     'organization': organization,
                                                                     'custom_page_range': custom_page_range,
                                                                     'section': 'courses_by_organization'})


def course_list(request):
    object_list = Course.published.all().select_related()
    courses, custom_page_range = paginate(request, object_list)
    # sponsored
    sponsored_courses = object_list.filter(is_ad=True)
    sp_courses_list = list(sponsored_courses)[:3]
    shuffle(sp_courses_list)
    return render(request, 'catalog/course/list.html', {'courses': courses,
                                                        'sponsored_courses': sp_courses_list,
                                                        'custom_page_range': custom_page_range,
                                                        'section': 'courses'})


@login_required
def organization_register(request):
    if request.method == 'POST':
        form = RegisterOrganizationForm(data=request.POST)
        if form.is_valid():
            org_name = form.cleaned_data['name']
            organization = form.save(commit=False)
            organization.slug = slugify(org_name)  # TODO: can be done in model?
            organization.save()
            request.user.organization = organization
            request.user.role = User.Roles.COORDINATOR
            request.user.save()
            messages.add_message(request, messages.SUCCESS, f'Organizace "{org_name}" úspěšně zaregistrována!')
            return redirect(dashboard)
        else:
            messages.add_message(request, messages.ERROR, 'Chyba při pokusu zaregistrovat organizaci!')
    else:
        form = RegisterOrganizationForm()
    return render(request, 'catalog/organization/register.html', {'form': form})


@login_required
def organization_update(request):
    user_organization = request.user.organization
    form = UpdateOrganizationForm(instance=user_organization)
    if request.method == 'POST':
        form = UpdateOrganizationForm(data=request.POST, instance=user_organization)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Údaje organizace upraveny!')
            return redirect(dashboard)
        else:
            messages.add_message(request, messages.ERROR, 'Chyba při pokusu upravit údaje organizace!')
    return render(request, 'catalog/organization/update.html', {'form': form, 'user_organization': user_organization})


@login_required
def organization_rename(request):
    user_organization = request.user.organization
    form = RenameOrganizationForm(instance=user_organization)
    if request.method == 'POST':
        form = RenameOrganizationForm(data=request.POST, instance=user_organization)
        if form.is_valid():
            name = form.cleaned_data['name']
            user_organization.name = name
            user_organization.slug = slugify(name)
            user_organization.save()
            messages.add_message(request, messages.SUCCESS, f'Organizace úspěšně přejmenována na "{name}"!')
            return redirect(dashboard)
        else:
            messages.add_message(request, messages.ERROR, 'Chyba při pokusu přejmenovat organizaci!')
    return render(request, 'catalog/organization/rename.html', {'form': form, 'user_organization': user_organization})


@login_required
def organization_delete(request):
    user_organization = request.user.organization
    if request.method == 'POST':
        request.user.role = User.Roles.STUDENT
        request.user.save()
        # todo: change status of all teachers to 'student' as well

        user_organization.delete()
        messages.add_message(request, messages.INFO, 'Organizace byla odstraněna.')
        return redirect(dashboard)
    return render(request, 'catalog/organization/delete.html', {'user_organization': user_organization})


@login_required
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(data=request.POST, files=request.FILES)  # 'files' includes image upload
        if form.is_valid():
            cd = form.cleaned_data
            course = form.save(commit=False)
            course.organization = request.user.organization
            course.name = cd['name'].capitalize()
            course.save()
            form.save_m2m()  # save tags
            post_process_image(form.cleaned_data, course)
            course_url_admin = request.build_absolute_uri(course.get_absolute_url_admin())
            mail_managers(f'Nová aktivita - čeká na schválení',
                          f'Název aktivity:\n{course.name}\n\n{course_url_admin}')
            messages.add_message(request, messages.SUCCESS, 'Aktivita byla úspěšně vytvořena a odeslána ke schválení!')
            return redirect(course.get_absolute_url())
        else:
            messages.add_message(request, messages.ERROR, 'Chyba při pokusu zaregistrovat aktivitu!')
    else:
        form = CourseForm()
        check_teacher_field(form, request)
    return render(request, 'catalog/course/create.html', {'form': form})


@login_required
def oneoff_course_create(request):
    if request.method == 'POST':
        form = OneoffCourseForm(data=request.POST, files=request.FILES)  # 'files' includes image upload
        if form.is_valid():
            cd = form.cleaned_data
            course = form.save(commit=False)
            course.organization = request.user.organization
            course.name = cd['name'].capitalize()
            course.date_from = datetime.combine(cd.get('date_from'), cd.get('time_from'))
            course.date_to = datetime.combine(cd.get('date_from'), cd.get('time_to'))
            course.is_oneoff = True
            course.save()
            form.save_m2m()
            post_process_image(cd, course)
            course_url_admin = request.build_absolute_uri(course.get_absolute_url_admin())
            mail_managers(f'Nová aktivita - čeká na schválení',
                          f'Název aktivity:\n{course.name}\n\n{course_url_admin}')
            messages.add_message(request, messages.SUCCESS,
                                 'Jednodenní aktivita byla úspěšně vytvořena a odeslána ke schválení!')
            return redirect(course.get_absolute_url())
        else:
            messages.add_message(request, messages.ERROR, 'Chyba při pokusu zaregistrovat jednodenní aktivitu!')
    else:
        form = OneoffCourseForm()
        check_teacher_field(form, request)
    return render(request, 'catalog/course/create_oneoff.html', {'form': form})


@login_required
def course_update(request, slug=None):
    course = get_object_or_404(Course, slug=slug)
    original_name, original_desc = course.name, course.description
    form = CourseForm(instance=course)
    form.fields['teacher'].queryset = User.objects.filter(organization_id=request.user.organization.id)
    if request.method == 'POST':
        # 'instance' parameter to relate to the existing object!
        form = CourseForm(data=request.POST, files=request.FILES, instance=course)
        if form.is_valid():
            cd = form.cleaned_data
            course = form.save(commit=False)
            approval_requested = is_approval_requested(cd, course, original_desc, original_name, request)
            course.save()
            form.save_m2m()
            post_process_image(form.cleaned_data, course)
            if approval_requested:
                messages.add_message(request, messages.SUCCESS,
                                     'Aktivita byla úspěšně upravena a odeslána ke schválení!')
            else:
                messages.add_message(request, messages.SUCCESS, 'Aktivita byla úspěšně upravena!')
            return redirect(course.get_absolute_url())
        else:
            messages.add_message(request, messages.ERROR, 'Chyba při pokusu upravit aktivitu!')
    return render(request, 'catalog/course/update.html', {'form': form})


@login_required
def oneoff_course_update(request, slug=None):
    course = get_object_or_404(Course, slug=slug)
    original_name, original_desc = course.name, course.description
    form = OneoffCourseForm(instance=course)
    form.fields['time_from'].initial = localtime(course.date_from).strftime('%H:%M')
    form.fields['time_to'].initial = localtime(course.date_to).strftime('%H:%M')
    form.fields['teacher'].queryset = User.objects.filter(organization_id=request.user.organization.id)
    if request.method == 'POST':
        # 'instance' parameter to relate to the existing object!
        form = OneoffCourseForm(data=request.POST, files=request.FILES, instance=course)
        if form.is_valid():
            cd = form.cleaned_data
            course = form.save(commit=False)
            # TODO: do not hit db if unnecessary
            course.date_from = datetime.combine(cd.get('date_from'), cd.get('time_from'))
            course.date_to = datetime.combine(cd.get('date_from'), cd.get('time_to'))
            approval_requested = is_approval_requested(cd, course, original_desc, original_name, request)
            course.save()
            form.save_m2m()
            post_process_image(cd, course)
            if approval_requested:
                messages.add_message(request, messages.SUCCESS,
                                     'Jednodenní aktivita byla úspěšně upravena a odeslána ke schválení!')
            else:
                messages.add_message(request, messages.SUCCESS, 'Jednodenní aktivita byla úspěšně upravena!')
            return redirect(course.get_absolute_url())
        else:
            messages.add_message(request, messages.ERROR, 'Chyba při pokusu upravit aktivitu!')
    return render(request, 'catalog/course/update_oneoff.html', {'form': form})


def course_detail(request, slug=None):
    course = get_object_or_404(Course.objects.select_related(), slug=slug)
    if course.status == Course.Status.DRAFT and course.organization != request.user.organization:
        raise PermissionDenied
    form = ContactTeacherForm()
    price_hour = round(course.price / course.hours)

    week_schedule = defaultdict(list)
    for j in range(7, 23):  # create empty schedule
        for i in range(7):
            week_schedule[j].append(' ')
    for i in course.week_schedule.all():
        week_schedule[i.hour][i.day_of_week] = 'X'
    week_schedule = dict(week_schedule)
    return render(request, 'catalog/course/detail.html', {'course': course,
                                                          'form': form,
                                                          'price_hour': price_hour,
                                                          'schedule': week_schedule})


@login_required
def course_delete(request, slug=None):
    course = get_object_or_404(Course, slug=slug)
    if request.method == 'POST':
        course.delete()
        messages.add_message(request, messages.INFO, 'Aktivita byla odstraněna.')
        return redirect('course_list_by_organization', slug=request.user.organization.slug)
    return render(request, 'catalog/course/delete.html', {'course_name': course.name})


def contact_teacher(request, slug=None):
    course = get_object_or_404(Course, slug=slug)
    if request.method == 'POST':
        form = ContactTeacherForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            course_url = request.build_absolute_uri(course.get_absolute_url())
            subject = f'{cd["sender_name"]} má dotaz k {course.name}'
            body = f'Uživatel "{cd["sender_name"].capitalize()}" vám zaslal dotaz k aktivitě {course.name.upper()}\n' \
                   f'(odkaz: {course_url})\n' \
                   f'E-mailová adresa pro odpověd: {cd["from_email"]}\n\n' \
                   f'Text dotazu:\n{cd["body"]}'
            email = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [course.teacher.email, ],
                                 reply_to=[cd["from_email"]], )
            email.send()
            messages.add_message(request, messages.SUCCESS, 'Dotaz na vedoucího byl odeslán!')
        else:
            messages.add_message(request, messages.ERROR, 'Chyba při odesílání dotazu!')
    return redirect(course.get_absolute_url())
