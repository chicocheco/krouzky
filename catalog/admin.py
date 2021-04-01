from django.contrib import admin
from django.db.models import ManyToManyField
from django.forms import CheckboxSelectMultiple
from tinymce.widgets import TinyMCE

from .forms import CourseAdminForm
from .models import Organization, Course, Topic, AgeCategory

admin.site.register(Organization)
admin.site.register(Topic)
admin.site.register(AgeCategory)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    form = CourseAdminForm
    formfield_overrides = {
        ManyToManyField: {'widget': CheckboxSelectMultiple},
    }
    list_display = ('name', 'slug', 'teacher', 'organization', 'status')
    list_filter = ('status', 'teacher', 'organization')
    search_fields = ('name', 'description')
    date_hierarchy = 'date_modified'
    ordering = ('status', 'date_modified')
    widgets = {
        'description': TinyMCE(),
    }
