import django_filters
from crispy_forms.bootstrap import InlineCheckboxes, AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Row, Column
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

from .models import Course, Topic, WeekSchedule

"""
Notes for week_day filter:
week_day filter equals more or less this:
week_days = request.GET.getlist('week_day')
object_list = Course.published.filter(week_schedule__day_of_week__in=week_days).distinct()
"""


def filter_by_query(queryset, _, value):
    search_vector = SearchVector('name__unaccent', weight='A') + \
                    SearchVector('description__unaccent', weight='B')
    search_query = SearchQuery(value)
    return queryset.annotate(
        search=search_vector,
        rank=SearchRank(search_vector, search_query)).filter(rank__gte=0.3).order_by('-rank')


class CourseFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(label='Klíčové slovo', method=filter_by_query)
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte', label='Minimální cena aktivity',
                                            help_text='Zvolte násobky 100')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte', label='Maximální cena aktivity')
    topic = django_filters.ModelMultipleChoiceFilter(queryset=Topic.objects.all(),
                                                     field_name='topic',
                                                     lookup_expr='exact',
                                                     label='Omezit výběr zaměření')
    week_day = django_filters.MultipleChoiceFilter(choices=WeekSchedule.WeekDay.choices,
                                                   field_name='week_schedule__day_of_week',
                                                   lookup_expr='in',  # choices get collected in a list
                                                   distinct=True,
                                                   conjoined=False,
                                                   label='Den v týdnu')
    date_from = django_filters.DateFilter(input_formats=['%d.%m.%Y'], lookup_expr='gte', label='Od data',
                                          help_text='Kliknutím se otevře kalendář')
    date_to = django_filters.DateFilter(input_formats=['%d.%m.%Y'], lookup_expr='lte', label='Do data')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.helper = FormHelper()
        self.form.helper.disable_csrf = True
        self.form.helper.form_tag = False
        self.form.helper.form_show_labels = True
        self.form.helper.form_show_errors = False
        self.form.helper.layout = Layout(Field('q', css_class='col-12'),
                                         Row(
                                             Column(AppendedText('price_min', 'Kč')),
                                             Column(AppendedText('price_max', 'Kč')),
                                             Column('age_category')
                                         ),
                                         Row(
                                             Column('date_from'),
                                             Column('date_to')
                                         ),
                                         InlineCheckboxes('topic', css_class='col-12'),
                                         InlineCheckboxes('week_day', css_class='col-12'),
                                         )
        # TODO: self.form.fields['price_min'].initial = 0
        # TODO: self.form.fields['price_max'].initial = 0
        self.form.fields['price_min'].widget.attrs.update({'min': 0, 'max': 99999, 'step': 100})
        self.form.fields['price_max'].widget.attrs.update({'min': 0, 'max': 99999, 'step': 100})
        self.form.fields['age_category'].empty_label = 'Bez omezení'

    class Meta:
        model = Course
        # query, price, topic, age_category, datem_from, date_to
        fields = ['age_category']  # this works only as fallback
