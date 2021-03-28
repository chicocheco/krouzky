from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Organization, Course, Topic, AgeCategory

admin.site.register(Organization)
admin.site.register(Topic)
admin.site.register(AgeCategory)


# @admin.register(Course)
# class CourseAdmin(admin.ModelAdmin):
#     list_display = ('name', 'slug', 'teacher', 'organization', 'status')
#     list_filter = ('status', 'teacher', 'organization')
#     search_fields = ('name', 'description')
#     date_hierarchy = 'date_modified'
#     ordering = ('status', 'date_modified')

@admin.register(Course)
class SomeModelAdmin(SummernoteModelAdmin):  # instead of ModelAdmin
    summernote_fields = '__all__'
    list_display = ('name', 'slug', 'teacher', 'organization', 'status')
    list_filter = ('status', 'teacher', 'organization')
    search_fields = ('name', 'description')
    date_hierarchy = 'date_modified'
    ordering = ('status', 'date_modified')
