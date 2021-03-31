import django_filters
from crispy_forms.bootstrap import InlineCheckboxes, AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Row, Column
from django import forms

from .models import Course, Topic


class CourseFilter(django_filters.FilterSet):
    query = django_filters.CharFilter(label='Klíčové slovo')
    price_start = django_filters.NumberFilter(field_name='price', lookup_expr='gte', label='Cena od')
    price_stop = django_filters.NumberFilter(field_name='price', lookup_expr='lte', label='Cena do')
    topic = django_filters.ModelMultipleChoiceFilter(queryset=Topic.objects.all(),
                                                     widget=forms.CheckboxSelectMultiple,
                                                     label='Omezit výběr zaměření')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.helper = FormHelper()
        self.form.helper.disable_csrf = True
        self.form.helper.form_tag = False
        self.form.helper.form_show_labels = True
        self.form.helper.form_show_errors = False
        self.form.helper.layout = Layout(Field('query', css_class='col-12'),
                                         Row(
                                             Column(AppendedText('price_start', 'Kč'), css_class='col-4'),
                                             Column(AppendedText('price_stop', 'Kč'), css_class='col-4'),
                                             Column(Field('age_category', css_class='col-12'), css_class='col-4')
                                         ),
                                         InlineCheckboxes('topic', css_class='col-12'), )
        self.form.fields['price_start'].widget.attrs.update({'min': 0, 'step': 100})
        self.form.fields['price_stop'].widget.attrs.update({'min': 0, 'step': 100})
        self.form.fields['age_category'].empty_label = 'Bez omezení'

    class Meta:
        model = Course
        # query, price, topic, age_category
        fields = ['age_category']  # this works only as fallback
