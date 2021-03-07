from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import OrganizationForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import Course


def home(request):
    return render(request, 'catalog/home.html')


@login_required
def edit_organization(request):
    if request.method == 'POST':
        organization_form = OrganizationForm(data=request.POST)
        if organization_form.is_valid():
            new_org = organization_form.save(commit=False)
            request.user.organization = new_org
            request.user.role = 'COORDINATOR'
            new_org.save()
            request.user.save()
            messages.add_message(request, messages.SUCCESS, 'Informace o organizaci uložena!')
            return render(request, 'catalog/home.html')
    else:
        if request.user.organization:
            organization_form = OrganizationForm(instance=request.user.organization)
        else:
            organization_form = OrganizationForm()
    return render(request, 'catalog/organization/edit.html',
                  {'organization_form': organization_form})


@login_required
def dashboard(request):
    return render(request, 'catalog/dashboard.html')


def list_courses(request):
    object_list = Course.objects.all()
    paginator = Paginator(object_list, 10)
    page = request.GET.get('page')
    try:
        courses = paginator.page(page)
    except PageNotAnInteger:
        courses = paginator.page(1)
    except EmptyPage:
        courses = paginator.page(paginator.num_pages)
    return render(request, 'catalog/course/list.html', {'page': page, 'courses': courses})
