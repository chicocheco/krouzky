from django.contrib import admin

from .models import Organization, Course, Topic, AgeCategory

admin.site.register(Organization)
admin.site.register(Course)
admin.site.register(Topic)
admin.site.register(AgeCategory)
