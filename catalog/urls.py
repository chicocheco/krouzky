from django.urls import path

from . import views as catalog_views

urlpatterns = [
    path('', catalog_views.home, name='home'),
    path('muj-ucet/', catalog_views.dashboard, name='dashboard'),
    path('organizace/registrovat', catalog_views.register_organization, name='register_organization'),
    path('organizace/upravit', catalog_views.update_organization, name='update_organization'),
    path('organizace/prejmenovat', catalog_views.rename_organization, name='rename_organization'),
    path('organizace/<slug:slug>/krouzky/', catalog_views.course_list, name='course_list_organization'),
    path('krouzky/', catalog_views.course_list, name='course_list'),
    path('o-nas/', catalog_views.about_us, name='about_us')
]
