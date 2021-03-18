from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import UserUpdateForm


@login_required
def update(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(data=request.POST, files=request.FILES, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Profil byl úspěšně upraven!')
        else:
            messages.error(request, 'Chyba při pokusu upravit profil!')
        return redirect('dashboard')
    else:
        user_form = UserUpdateForm(instance=request.user)
    return render(request, 'account/update.html', {'user_form': user_form})
