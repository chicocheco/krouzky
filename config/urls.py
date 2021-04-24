import debug_toolbar
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('spravce/', admin.site.urls),
    path('ucet/', include('users.urls')),  # customized czech urls of allauth
    # path('ucet/', include('allauth.urls')),  # fallback
    path('', include('catalog.urls')),
    path('tinymce/', include('tinymce.urls')),
    path('__debug__/', include(debug_toolbar.urls)),
]

if settings.DEBUG:  # local development only
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
