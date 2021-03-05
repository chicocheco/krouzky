from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import OrganizationForm


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
