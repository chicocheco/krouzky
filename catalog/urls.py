from django.urls import path

from . import views as catalog_views

urlpatterns = [
    path('', catalog_views.home, name='home'),
    path('muj-ucet/', catalog_views.dashboard, name='dashboard'),
    path('organizace/registrovat', catalog_views.organization_register, name='organization_register'),
    path('organizace/upravit', catalog_views.organization_update, name='organization_update'),
    path('organizace/prejmenovat', catalog_views.organization_rename, name='organization_rename'),
    path('organizace/<slug:slug>/krouzky/', catalog_views.course_list, name='course_list_by_organization'),

    path('krouzky/', catalog_views.course_list, name='course_list'),
    # path('krouzky/<slug:slug>/', catalog_views.course_detail, name='course_detail'),
    path('o-nas/', catalog_views.about_us, name='about_us')
]
