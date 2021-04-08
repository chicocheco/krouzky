from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify

from users.models import User
from .forms import (UpdateOrganizationForm, RenameOrganizationForm, RegisterOrganizationForm, CourseForm,
                    OneoffCourseForm, ContactTeacherForm, SimpleSearchForm)
from .models import Course, Organization
from .filters import CourseFilter


def home(request):
    form = SimpleSearchForm()
    return render(request, 'catalog/home.html', {'form': form})


def cooperation(request):
    return render(request, 'catalog/cooperation.html', {'section': 'cooperation'})


@login_required
def dashboard(request):
    return render(request, 'catalog/dashboard.html')


def course_list(request, slug=None):
    if slug:
        organization = get_object_or_404(Organization, slug=slug)
        if not request.user.is_authenticated:
            return redirect('home')
        if organization != request.user.organization:  # display 403 (todo: custom template)
            raise PermissionDenied()
        organization_name = organization.name
        object_list = Course.objects.filter(organization=organization)
    else:
        organization_name = None
        object_list = Course.published.all()
    paginator = Paginator(object_list, 10)
    page = request.GET.get('page')
    try:
        courses = paginator.page(page)
    except PageNotAnInteger:
        courses = paginator.page(1)
    except EmptyPage:
        courses = paginator.page(paginator.num_pages)
    return render(request, 'catalog/course/list.html',
                  {'page': page, 'courses': courses, 'organization_name': organization_name,
                   'section': 'courses'})


def about_us(request):
    return render(request, 'catalog/about.html', {'section': 'about_us'})


@login_required
def organization_register(request):
    if request.method == 'POST':
        form = RegisterOrganizationForm(data=request.POST)
        if form.is_valid():
            org_name = form.cleaned_data['name']
            organization = form.save(commit=False)
            organization.slug = slugify(org_name)
            organization.save()
            request.user.organization = organization
            request.user.role = User.Roles.COORDINATOR
            request.user.save()
            messages.add_message(request, messages.SUCCESS, f'Organizace "{org_name}" zaregistrována!')
        return redirect(dashboard)
    else:
        form = RegisterOrganizationForm()
    return render(request, 'catalog/organization/register.html', {'form': form})


@login_required
def organization_update(request):
    form = UpdateOrganizationForm(instance=request.user.organization)
    if request.method == 'POST':
        form = UpdateOrganizationForm(data=request.POST, instance=request.user.organization)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Údaje organizace upraveny!')
        else:
            messages.add_message(request, messages.ERROR, 'Chyba při pokusu upravit údaje organizace!')
        return redirect(dashboard)
    return render(request, 'catalog/organization/update.html', {'form': form})


@login_required
def organization_rename(request):
    if request.method == 'POST':
        form = RenameOrganizationForm(data=request.POST)
        if form.is_valid():
            org_name = form.cleaned_data['name']
            organization = request.user.organization
            organization.name = org_name
            organization.slug = slugify(org_name)
            organization.save()
            messages.add_message(request, messages.SUCCESS, f'Organizace přejmenována na {org_name}.')
            return redirect(dashboard)
    else:
        form = RenameOrganizationForm(instance=request.user.organization)
    return render(request, 'catalog/organization/rename.html', {'form': form})


@login_required
def organization_delete(request):
    if request.method == 'POST':
        request.user.role = User.Roles.STUDENT
        request.user.save()
        # todo: change status of all teachers to 'student' as well

        request.user.organization.delete()
        messages.add_message(request, messages.SUCCESS, 'Organizace byla odstraněna.')
        return redirect(dashboard)
    return render(request, 'catalog/organization/delete.html')


@login_required
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(data=request.POST, files=request.FILES)  # 'files' includes image upload
        if form.is_valid():
            course = form.save(commit=False)
            course.organization = request.user.organization
            course.save()
            form.save_m2m()  # save Topic
            messages.add_message(request, messages.SUCCESS, 'Aktivita byla úspěšně vytvořena a odeslána ke schválení!')
        else:
            messages.add_message(request, messages.ERROR, 'Chyba při pokusu zaregistrovat aktivitu!')
        return redirect(dashboard)
    else:
        form = CourseForm()
        teacher_field = form.fields['teacher']
        teachers = User.objects.filter(organization_id=request.user.organization.id)
        teacher_field.queryset = teachers
        if len(teachers) == 1:
            teacher_field.disabled = True
    return render(request, 'catalog/course/create.html', {'form': form})


@login_required
def course_create_oneoff(request):
    if request.method == 'POST':
        form = OneoffCourseForm(data=request.POST, files=request.FILES)  # 'files' includes image upload
        if form.is_valid():
            course = form.save(commit=False)
            course.organization = request.user.organization
            course.save()
            form.save_m2m()  # save Topic
            messages.add_message(request, messages.SUCCESS,
                                 'Jednodenní aktivita byla úspěšně vytvořena a odeslána ke schválení!')
        else:
            print(form.errors)
            messages.add_message(request, messages.ERROR,
                                 'Chyba při pokusu zaregistrovat jednodenní aktivitu!')
        return redirect(dashboard)
    else:
        form = OneoffCourseForm()
        teacher_field = form.fields['teacher']
        teachers = User.objects.filter(organization_id=request.user.organization.id)
        teacher_field.queryset = teachers
        if len(teachers) == 1:
            teacher_field.disabled = True
    return render(request, 'catalog/course/create_oneoff.html', {'form': form})


@login_required
def course_update(request, slug=None):
    course = get_object_or_404(Course, slug=slug)
    form = CourseForm(instance=course)
    form.fields['teacher'].queryset = User.objects.filter(organization_id=request.user.organization.id)
    if request.method == 'POST':
        # 'instance' parameter to relate to the existing object!
        form = CourseForm(data=request.POST, files=request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Aktivita byla úspěšně upravena!')
        else:
            messages.add_message(request, messages.ERROR, 'Chyba při pokusu upravit aktivitu!')
        return redirect(dashboard)
    return render(request, 'catalog/course/update.html', {'form': form})


def course_detail(request, slug=None):
    course = get_object_or_404(Course, slug=slug)
    form = ContactTeacherForm()
    price_hour = round(course.price / course.hours)
    return render(request, 'catalog/course/detail.html', {'course': course, 'form': form, 'price_hour': price_hour})


@login_required
def course_delete(request, slug=None):
    course = get_object_or_404(Course, slug=slug)
    course_name = course.name
    if request.method == 'POST':
        course.delete()
        messages.add_message(request, messages.SUCCESS, 'Organizace byla odstraněna!')
        return redirect(dashboard)
    return render(request, 'catalog/course/delete.html', {'course_name': course_name})


def contact_teacher(request, slug=None):
    course = get_object_or_404(Course, slug=slug)
    if request.method == 'POST':
        form = ContactTeacherForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            course_url = request.build_absolute_uri(course.get_absolute_url())
            subject = f'{cd["sender_name"]} má dotaz k {course.name}'
            message = f'Uživatel/ka {cd["sender_name"].upper()} vám zaslal/a dotaz k aktivitě {course.name.upper()}\n' \
                      f'(odkaz: {course_url})' \
                      f'\n\nText dotazu:\n{cd["body"]}'
            send_mail(subject, message, cd['from_email'], [course.teacher.email, ])
            messages.add_message(request, messages.SUCCESS, 'Dotaz byl odeslán!')
        else:
            messages.add_message(request, messages.ERROR, 'Chyba při odesílání dotazu!')
    return redirect(course.get_absolute_url())


def search(request):
    query = None
    f = CourseFilter(request.GET, Course.published.all())
    if 'query' in request.GET:
        form = SimpleSearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('name', weight='A') + \
                            SearchVector('description', weight='B')
            search_query = SearchQuery(query)
            object_list = Course.published.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)).filter(rank__gte=0.3).order_by('-rank')
            queryset = request.GET.copy()
            queryset.pop('query')
            f = CourseFilter(queryset, object_list)
    return render(request, 'catalog/course/search.html', {'filter': f, 'query': query, 'section': 'search'})
