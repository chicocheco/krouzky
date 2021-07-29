from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage, mail_managers
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from django.utils.timezone import localtime, make_aware

from invitations.forms import InviteTeacherForm
from invitations.models import Invitation
from .filters import CourseFilter
from .forms import (UpdateOrganizationForm, RenameOrganizationForm, RegisterOrganizationForm, CourseForm,
                    OneoffCourseForm, ContactTeacherForm)
from .models import Course, Organization
from .utils import (is_approval_requested, post_process_image, check_teacher_field, paginate,
                    get_sponsored_courses_list, make_week_schedule)

User = get_user_model()


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
    """List of paginated courses that can be filtered. Every page includes sponsored courses at the top."""

    query = None
    qs = Course.published.all().select_related()
    sponsored_courses = get_sponsored_courses_list(qs)

    course_filter = CourseFilter(request.GET, qs)
    form = course_filter.form  # detach form for rendering
    if 'q' in request.GET:
        form.fields['q'].initial = request.GET.get('q')
    courses, custom_page_range, counter = paginate(request, course_filter.qs)
    return render(request, 'catalog/course/search.html', {'courses': courses,
                                                          'sponsored_courses': sponsored_courses,
                                                          'counter': counter,
                                                          'form': form,
                                                          'query': query,
                                                          'custom_page_range': custom_page_range,
                                                          'section': 'search'})


def course_list_by_organization(request, slug):
    """List of paginated courses belonging to a single organization."""

    organization = get_object_or_404(Organization, slug=slug)
    is_organization_of_user = False
    qs = Course.published.all().filter(organization=organization).select_related()
    if request.user.is_authenticated:
        qs = Course.objects.filter(organization=organization).select_related()
        is_organization_of_user = (request.user.organization == organization)
    courses, custom_page_range, counter = paginate(request, qs)
    return render(request, 'catalog/course/list_organization.html', {'courses': courses,
                                                                     'counter': counter,
                                                                     'organization': organization,
                                                                     'is_organization_of_user': is_organization_of_user,
                                                                     'custom_page_range': custom_page_range,
                                                                     'section': 'courses_by_organization'})


def course_list(request):
    """List of paginated courses including sponsored ones on the top on every page."""

    qs = Course.published.all().select_related()
    sponsored_courses = get_sponsored_courses_list(qs)
    courses, custom_page_range, counter = paginate(request, qs)
    return render(request, 'catalog/course/list.html', {'courses': courses,
                                                        'sponsored_courses': sponsored_courses,
                                                        'custom_page_range': custom_page_range,
                                                        'section': 'courses'})


@login_required
def organization_register(request):
    """Register an organization and assign it to the current user, changing their role on User model."""

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
            messages.add_message(request, messages.SUCCESS, f'Organizace "{org_name}" úspěšně zaregistrována!')
            return redirect(dashboard)
        else:
            messages.add_message(request, messages.ERROR, 'Chyba při pokusu zaregistrovat organizaci!')
    else:
        form = RegisterOrganizationForm()
    return render(request, 'catalog/organization/register.html', {'form': form})


@login_required
def organization_update(request):
    """Update any field of the organization except for its name and slug."""

    if request.user.role != User.Roles.COORDINATOR:
        raise PermissionDenied
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
    """Update name and the related slug field."""

    if request.user.role != User.Roles.COORDINATOR:
        raise PermissionDenied
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
    """
    Delete user's organization and change the the role of all members, if any, back to the default (STUDENT).
    This view is allowed only to users of a COORDINATOR role.
    """

    if request.user.role != User.Roles.COORDINATOR:
        raise PermissionDenied
    user_organization = request.user.organization
    if request.method == 'POST':
        update_queries = []
        for user in user_organization.users.all():
            user.role = User.Roles.STUDENT
            update_queries.append(user)
        User.objects.bulk_update(update_queries, ['role'])
        user_organization.delete()
        messages.add_message(request, messages.INFO, 'Organizace byla odstraněna.')
        return redirect(dashboard)
    return render(request, 'catalog/organization/delete.html', {'user_organization': user_organization})


@login_required
def organization_invite_teacher(request):
    """
    Send an e-mail invitation to user's organization. Invitation expires in 3 days.
    This view is allowed only to users of a COORDINATOR role.
    """

    if request.user.role != User.Roles.COORDINATOR:
        raise PermissionDenied
    user_organization = request.user.organization
    if request.method == 'POST':
        form = InviteTeacherForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            invite = Invitation.create(cd['invited_email'], inviter=request.user)
            invite.send_invitation(request)
            messages.add_message(request, messages.SUCCESS,
                                 f"Pozvánka zaslána na e-mailovou adresu {cd['invited_email']}.")
            return redirect(dashboard)
    else:
        form = InviteTeacherForm()
    return render(request, 'catalog/organization/invite.html', {'form': form, 'user_organization': user_organization})


@login_required
def organization_leave(request):
    """
    Leave user's organization and change the user's role back to the default (STUDENT).
    Only for users of a TEACHER role, because coordinators cannot leave their own organization - they delete it.
    """

    if request.user.role != User.Roles.TEACHER:
        raise PermissionDenied
    user_organization = request.user.organization
    if request.method == 'POST':
        request.user.role = User.Roles.STUDENT
        request.user.organization = None
        request.user.save()
        messages.add_message(request, messages.INFO, 'Opustil/a jste organizaci.')
        return redirect(dashboard)
    return render(request, 'catalog/organization/leave.html', {'user_organization': user_organization})


@login_required
def organization_members(request):
    """
    List of invited members, where all of them are of a TEACHER role.
    This view is allowed only to users of a COORDINATOR role.
    """

    if request.user.role != User.Roles.COORDINATOR:
        raise PermissionDenied
    user_organization = request.user.organization
    members = user_organization.users.all().exclude(pk=request.user.pk)
    return render(request, 'catalog/organization/members.html', {'user_organization': user_organization,
                                                                 'members': members})


@login_required
def organization_remove_member(request, pk):
    """
    Unassign a member from user's organization and change their role back to STUDENT.

    This is allowed only to a user of a COORDINATOR role. Also, the member to be removed must be a member of user's
    organization and they cannot remove themselves.
    """

    if request.user.role != User.Roles.COORDINATOR:
        raise PermissionDenied
    user_organization = request.user.organization
    member = get_object_or_404(User, pk=pk)  # TODO: switch to UUID for external use
    if member.organization != user_organization or member == request.user:
        raise PermissionDenied
    if request.method == 'POST':
        member.role = User.Roles.STUDENT
        member.organization = None
        member.save()
        messages.add_message(request, messages.INFO, 'Člen byl odebrán z organizace.')
        return redirect(dashboard)
    return render(request, 'catalog/organization/remove_member.html', {'user_organization': user_organization,
                                                                       'member': member})


@login_required
def course_create(request):
    """Create a regular course, assigning it to the user's organization and notify the managers about it by email."""

    if request.method == 'POST':
        form = CourseForm(data=request.POST, files=request.FILES)  # 'files' includes image upload
        if form.is_valid():
            course = form.save(commit=False)
            course.organization = request.user.organization
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
    """
    Create a one-off course, assigning it to the user's organization and notify the managers about it by email.
    In addition, populate date_from and date_to fields sharing the same date but different hour.
    """

    if request.method == 'POST':
        form = OneoffCourseForm(data=request.POST, files=request.FILES)  # 'files' includes image upload
        if form.is_valid():
            cd = form.cleaned_data
            course = form.save(commit=False)
            course.organization = request.user.organization
            course.date_from = make_aware(datetime.combine(cd.get('date_from'), cd.get('time_from')))
            course.date_to = make_aware(datetime.combine(cd.get('date_from'), cd.get('time_to')))
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
    """
    Update the regular course. If its name or description was changed, switch its status back to DRAFT and notify the
    managers about it.

    User of a TEACHER role can modify only courses that were assigned to them.
    """

    course = get_object_or_404(Course, slug=slug)
    if request.user.role == User.Roles.TEACHER and request.user != course.teacher or \
            request.user.organization != course.organization:
        raise PermissionDenied
    original_name, original_desc = course.name, course.description
    form = CourseForm(instance=course)
    check_teacher_field(form, request)
    if request.method == 'POST':
        form = CourseForm(data=request.POST, files=request.FILES, instance=course)
        if form.is_valid():
            course = form.save(commit=False)
            approval_requested = is_approval_requested(course, original_desc, original_name, request)
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
    """
    Update the one-off course. If its name or description was changed, switch its status back to DRAFT and notify the
    managers about it.

    In addition, decouple the datetime objects sharing the same date to be able to modify the hour only in the form.
    In order to avoid re-building these objects every time even when nothing was changed,
    compare the original hour values with the new ones.

    User of a TEACHER role can modify only courses that were assigned to them.
    """

    course = get_object_or_404(Course, slug=slug)
    if request.user.role == User.Roles.TEACHER and request.user != course.teacher or \
            request.user.organization != course.organization:
        raise PermissionDenied
    original_name, original_desc = course.name, course.description
    form = OneoffCourseForm(instance=course)
    original_time_from = localtime(course.date_from).strftime('%H:%M')
    original_time_to = localtime(course.date_to).strftime('%H:%M')
    form.fields['time_from'].initial = original_time_from
    form.fields['time_to'].initial = original_time_to
    check_teacher_field(form, request)
    if request.method == 'POST':
        form = OneoffCourseForm(data=request.POST, files=request.FILES, instance=course)
        if form.is_valid():
            cd = form.cleaned_data
            course = form.save(commit=False)
            if original_time_from != cd.get('time_from') or original_time_to != cd.get('time_to'):
                course.date_from = make_aware(datetime.combine(cd.get('date_from'), cd.get('time_from')))
                course.date_to = make_aware(datetime.combine(cd.get('date_from'), cd.get('time_to')))
            approval_requested = is_approval_requested(course, original_desc, original_name, request)
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
    """Course detail with a contact form of the assigned user to it (teacher)."""

    course = get_object_or_404(Course.objects.select_related(), slug=slug)
    if course.status != Course.Status.PUBLISHED:
        if request.user.is_authenticated and course.organization != request.user.organization \
                or not request.user.is_authenticated:
            raise PermissionDenied
    form = ContactTeacherForm()  # POST via contact_teacher view
    price_hour = round(course.price / course.hours)
    week_schedule = make_week_schedule(course)
    return render(request, 'catalog/course/detail.html', {'course': course,
                                                          'form': form,
                                                          'price_hour': price_hour,
                                                          'schedule': week_schedule})


@login_required
def course_delete(request, slug=None):
    """Delete course. User of a TEACHER role can delete only courses that were assigned to them."""

    course = get_object_or_404(Course, slug=slug)
    if request.user.role == User.Roles.TEACHER and request.user != course.teacher or \
            request.user.organization != course.organization:
        raise PermissionDenied
    if request.method == 'POST':
        course.delete()
        messages.add_message(request, messages.INFO, 'Aktivita byla odstraněna.')
        return redirect('course_list_by_organization', slug=request.user.organization.slug)
    return render(request, 'catalog/course/delete.html', {'course_name': course.name})


def contact_teacher(request, slug=None):
    """Contact the teacher (assigned account) of the course with an embedded URL."""

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
