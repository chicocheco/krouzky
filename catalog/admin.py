from django.contrib import admin
from django.db.models import ManyToManyField
from django.forms import CheckboxSelectMultiple
from tinymce.widgets import TinyMCE

from .forms import CourseAdminForm
from .models import Organization, Course, AgeCategory

admin.site.register(Organization)
admin.site.register(AgeCategory)

# admin.site.register(WeekSchedule)
admin.site.site_header = 'Správa webu vyberaktivitu.online'
admin.site.site_title = 'vyberaktivitu.online'
admin.site.index_title = 'Správa webu'


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
    ordering = ('-date_modified', 'status')
    widgets = {
        'description': TinyMCE(),
    }
    fields = (
        'name', 'status', 'tags', 'category', 'age_category', 'url', 'is_ad', 'price', 'hours',
        'capacity', 'date_from', 'date_to', 'teacher', 'organization', 'image', 'description'
    )
