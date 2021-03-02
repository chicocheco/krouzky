from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('spravce/', admin.site.urls),
    path('ucet/', include('allauth.urls')),
]
