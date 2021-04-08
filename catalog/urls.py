from django.urls import path

from . import views as catalog_views

urlpatterns = [
    path('', catalog_views.home, name='home'),
    path('prehled/', catalog_views.dashboard, name='dashboard'),
    path('organizace/registrovat', catalog_views.organization_register, name='organization_register'),
    path('organizace/upravit', catalog_views.organization_update, name='organization_update'),
    path('organizace/prejmenovat', catalog_views.organization_rename, name='organization_rename'),
    path('organizace/odstranit', catalog_views.organization_delete, name='organization_delete'),
    path('organizace/<slug:slug>/aktivity/', catalog_views.course_list, name='course_list_by_organization'),

    path('aktivity/', catalog_views.course_list, name='course_list'),
    path('aktivita/registrovat', catalog_views.course_create, name='course_create'),
    path('aktivita/registrovat-jednodenni', catalog_views.course_create_oneoff, name='course_create_oneoff'),
    path('aktivita/<slug:slug>/', catalog_views.course_detail, name='course_detail'),
    path('aktivita/<slug:slug>/dotaz', catalog_views.contact_teacher, name='course_contact_teacher'),
    # TODO: temporarily deactivated:
    # path('aktivita/<slug:slug>/upravit', catalog_views.course_update, name='course_update'),
    path('aktivita/<slug:slug>/odstranit', catalog_views.course_delete, name='course_delete'),
    path('o-nas/', catalog_views.about_us, name='about_us'),
    path('spoluprace/', catalog_views.cooperation, name='cooperation'),
    path('hledani/', catalog_views.search, name='search'),
]
