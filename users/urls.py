from django.urls import path, re_path

from allauth.account import views as allauth_views
from . import views as users_views

# czech urls of allauth
urlpatterns = [
    path('upravit', users_views.update, name='user_update'),

    path('registrace/', allauth_views.signup, name='account_signup'),
    path('prihlaseni/', allauth_views.login, name='account_login'),
    path('odhlaseni/', allauth_views.logout, name='account_logout'),
    path('heslo/zmenit/', allauth_views.password_change, name='account_change_password'),

    path("heslo/nastavit/", allauth_views.password_set, name="account_set_password"),
    path("neaktivni/", allauth_views.account_inactive, name="account_inactive"),

    # E-mail
    path('email/', allauth_views.email, name='account_email'),
    path('potvrdit-email/', allauth_views.email_verification_sent, name='account_email_verification_sent'),
    re_path(r'^potvrdit-email/(?P<key>[-:\w]+)/$', allauth_views.confirm_email, name='account_confirm_email'),

    # password reset
    path('heslo/reset/', allauth_views.password_reset, name='account_reset_password'),
    path('heslo/reset/hotovo/', allauth_views.password_reset_done, name='account_reset_password_done'),

    re_path(r'^heslo/reset/klic/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$', allauth_views.password_reset_from_key,
            name="account_reset_password_from_key"),
    path('heslo/reset/klic/hotovo/', allauth_views.password_reset_from_key_done,
         name='account_reset_password_from_key_done'),
]
