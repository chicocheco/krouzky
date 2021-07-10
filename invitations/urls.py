from django.urls import re_path, path

from . import views as invitations_views

urlpatterns = [
    re_path(r'^organizace/prijmout/(?P<key>\w+)/?$',
            invitations_views.AcceptInviteTeacher.as_view(), name='accept_invite_teacher'),
    path('prihlaseni/',
         invitations_views.AcceptExistingUserLoginView.as_view(), name='invited_account_login'),
]
