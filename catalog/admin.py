from django.contrib import admin

from .models import Organization, Course, Topic, AgeCategory

admin.site.register(Organization)
admin.site.register(Topic)
admin.site.register(AgeCategory)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'teacher', 'organization', 'status')
    list_filter = ('status', 'teacher', 'organization')
    search_fields = ('name', 'description')
    date_hierarchy = 'date_modified'
    ordering = ('status', 'date_modified')
