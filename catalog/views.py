from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
from django.utils.text import slugify

from users.models import User
from .forms import UpdateOrganizationForm, RenameOrganizationForm, RegisterOrganizationForm
from .models import Course, Organization


def home(request):
    return render(request, 'catalog/home.html')


@login_required
def dashboard(request):
    return render(request, 'catalog/dashboard.html')


def course_list(request, slug=None):
    if slug:
        organization = Organization.objects.get(slug=slug)
        organization_name = organization.name
        object_list = Course.objects.filter(organization=organization)
    else:
        organization_name = None
        object_list = Course.objects.all()
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
    if request.method == 'POST':
        organization_form = UpdateOrganizationForm(data=request.POST)
        if organization_form.is_valid():
            cd = organization_form.cleaned_data
            organization = request.user.organization
            organization.company_id = cd['company_id']
            organization.vat_id = cd['vat_id']
            organization.address = cd['address']
            organization.town = cd['town']
            organization.zip_code = cd['zip_code']
            organization.save()

            messages.add_message(request, messages.SUCCESS, 'Údaje organizace uloženy!')
            return redirect(dashboard)
    else:
        organization_form = UpdateOrganizationForm(instance=request.user.organization)
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
        # change status of all teachers to 'student' as well

        request.user.organization.delete()
        messages.add_message(request, messages.SUCCESS, f'Organizace odstraněna')
        return redirect(dashboard)
    return render(request, 'catalog/organization/delete.html')
