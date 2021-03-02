from django.urls import path, include

from . import views as catalog_views

urlpatterns = [
    path('', catalog_views.home, name='index'),
]
