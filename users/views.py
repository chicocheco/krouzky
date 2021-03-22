from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import UserUpdateForm, UserPhotoForm


@login_required
def update(request):
    if request.method == 'POST':
        form = UserUpdateForm(data=request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil byl úspěšně upraven!')
        else:
            messages.error(request, 'Chyba při pokusu upravit profil!')
        return redirect('dashboard')
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
