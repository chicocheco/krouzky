from django.urls import path

from . import views as catalog_views

urlpatterns = [
    path('', catalog_views.home, name='home'),
    path('muj-ucet/', catalog_views.dashboard, name='dashboard'),
    path('organizace/upravit', catalog_views.edit_organization, name='organization_edit'),
    path('krouzky/', catalog_views.course_list, name='course_list'),
    path('o-nas/', catalog_views.about_us, name='about_us')
]
