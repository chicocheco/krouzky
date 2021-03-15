from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify

from users.models import User
from .forms import UpdateOrganizationForm, RenameOrganizationForm, RegisterOrganizationForm, CourseForm
from .models import Course, Organization


def home(request):
    return render(request, 'catalog/home.html')


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
                  {'page': page, 'courses': courses, 'organization_name': organization_name, 'section': 'courses'})


def about_us(request):
    return render(request, 'catalog/about.html', {'section': 'about_us'})


@login_required
def organization_register(request):
    if request.method == 'POST':
        organization_form = RegisterOrganizationForm(data=request.POST)
        if organization_form.is_valid():
            org_name = organization_form.cleaned_data['name']
            organization = organization_form.save(commit=False)
            organization.slug = slugify(org_name)
            organization.save()
            request.user.organization = organization
            request.user.role = User.Roles.COORDINATOR
            request.user.save()
            messages.add_message(request, messages.SUCCESS, f'Organizace "{org_name}" zaregistrována!')
            return redirect(dashboard)
    else:
        organization_form = RegisterOrganizationForm()
    return render(request, 'catalog/organization/register.html', {'organization_form': organization_form})


@login_required
def organization_update(request):
    organization_form = UpdateOrganizationForm(instance=request.user.organization)
    if request.method == 'POST':
        organization_form = UpdateOrganizationForm(data=request.POST, instance=request.user.organization)
        if organization_form.is_valid():
            organization_form.save()
            messages.add_message(request, messages.SUCCESS, 'Údaje organizace upraveny!')
            return redirect(dashboard)
        else:
            messages.add_message(request, messages.SUCCESS, 'Chyba při pokusu upravit údaje organizace')
            return redirect(dashboard)
    return render(request, 'catalog/organization/update.html', {'organization_form': organization_form})


@login_required
def organization_rename(request):
    if request.method == 'POST':
        organization_form = RenameOrganizationForm(data=request.POST)
        if organization_form.is_valid():
            org_name = organization_form.cleaned_data['name']
            organization = request.user.organization
            organization.name = org_name
            organization.slug = slugify(org_name)
            organization.save()
            messages.add_message(request, messages.SUCCESS, f'Organizace přejmenována na {org_name}')
            return redirect(dashboard)
    else:
        organization_form = RenameOrganizationForm(instance=request.user.organization)
    return render(request, 'catalog/organization/rename.html', {'organization_form': organization_form})


@login_required
def organization_delete(request):
    if request.method == 'POST':
        request.user.role = User.Roles.STUDENT
        request.user.save()
        # todo: change status of all teachers to 'student' as well

        request.user.organization.delete()
        messages.add_message(request, messages.SUCCESS, 'Organizace byla odstraněna')
        return redirect(dashboard)
    return render(request, 'catalog/organization/delete.html')


@login_required
def course_create(request):
    if request.method == 'POST':
        course_form = CourseForm(data=request.POST, files=request.FILES)  # 'files' includes image upload
        if course_form.is_valid():
            course = course_form.save(commit=False)
            course.organization = request.user.organization
            course.save()
            course_form.save_m2m()  # save Topic
            messages.add_message(request, messages.SUCCESS, 'Kroužek byl úspěšně vytvořen a odeslán ke schválení!')
            return redirect(dashboard)
        else:
            messages.add_message(request, messages.ERROR, 'Chyba při pokusu zaregistrovat kroužek!')
            return redirect(dashboard)
    else:
        course_form = CourseForm()
        course_form.fields['teacher'].queryset = User.objects.filter(organization_id=request.user.organization.id)
    return render(request, 'catalog/course/create.html', {'course_form': course_form})


@login_required
def course_update(request, slug=None):
    course = get_object_or_404(Course, slug=slug)
    course_form = CourseForm(instance=course)
    course_form.fields['teacher'].queryset = User.objects.filter(organization_id=request.user.organization.id)
    if request.method == 'POST':
        # 'instance' parameter to relate to the existing object!
        course_form = CourseForm(data=request.POST, files=request.FILES, instance=course)
        if course_form.is_valid():
            course_form.save()
            messages.add_message(request, messages.SUCCESS, 'Kroužek byl úspěšně upraven!')
            return redirect(dashboard)
        else:
            messages.add_message(request, messages.ERROR, 'Chyba při pokusu upravit kroužek!')
            return redirect(dashboard)
    return render(request, 'catalog/course/update.html', {'course_form': course_form})


def course_detail(request, slug=None):
    course = get_object_or_404(Course, slug=slug)
    return render(request, 'catalog/course/detail.html', {'course': course})


def course_delete(request, slug=None):
    course = get_object_or_404(Course, slug=slug)
    course_name = course.name
    if request.method == 'POST':
        course.delete()
        messages.add_message(request, messages.SUCCESS, 'Organizace byla odstraněna')
        return redirect(dashboard)
    return render(request, 'catalog/course/delete.html', {'course_name': course_name})
