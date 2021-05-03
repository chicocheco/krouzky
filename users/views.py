from allauth.account.models import EmailAddress
from allauth.account.views import PasswordResetFromKeyView
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from .forms import UserUpdateForm, UserPhotoForm


class CustomPasswordResetFromKeyView(PasswordResetFromKeyView):
    success_url = reverse_lazy("dashboard")


@login_required
def update(request):
    original_email = request.user.email
    if request.method == 'POST':
        form = UserUpdateForm(data=request.POST, instance=request.user)
        if form.is_valid():
            cd = form.cleaned_data
            form.save()
            messages.success(request, 'Profil byl úspěšně upraven!')
            if original_email != cd['email']:
                email_address = EmailAddress.objects.get_for_user(user=request.user, email=original_email)
                email_address.change(request, cd['email'], confirm=True)  # re-sends confirmation
                logout(request)
                messages.info(request, f'Ověření nového e-mailu posláno na {cd["email"]}.')  # overrides default msg!
                # TODO: maybe shouldn't use the same template as when signing up
                return redirect('account_email_verification_sent')
            return redirect('dashboard')
        else:
            messages.error(request, 'Chyba při pokusu upravit profil!')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'account/update.html', {'form': form})


@login_required
def photo(request):
    if request.method == 'POST':
        form = UserPhotoForm(data=request.POST, files=request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profilová fotografie byla úspěšně nahrána!')
        else:
            messages.error(request, 'Chyba při pokusu nahrát fotografii!')
        return redirect('user_photo')
    else:
        form = UserPhotoForm(instance=request.user)
    return render(request, 'account/photo.html', {'form': form})


@login_required
def photo_delete(request):
    if request.method == 'POST':
        request.user.photo = None
        request.user.save()
        messages.success(request, 'Profilová fotografie byla úspěšně odstraněna!')
        return redirect('dashboard')
    return render(request, 'account/photo_delete.html')
