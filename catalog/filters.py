import django_filters
from crispy_forms.bootstrap import InlineCheckboxes, AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Row, Column, HTML, Div
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import Q

from .models import Course, WeekSchedule, AgeCategory
from .utils import get_slugs, asciify

"""
Notes for week_day filter:
week_day filter equals more or less this:
week_days = request.GET.getlist('week_day')
object_list = Course.published.filter(week_schedule__day_of_week__in=week_days).distinct()
"""


def filter_by_query(queryset, _, value):
    """
    Case and accent insensitive search in 'name', 'description' and tags.

    Remove accents from the string and fulltext search through unaccented columns 'name' and 'description'.
    Get a list of slugs based off of the string and search in tags. Order both queries by rank so fulltext results have
    always priority ('name' > 'description').
    """

    value = asciify(value)
    search_vector = SearchVector('name__unaccent', weight='A') + SearchVector('description__unaccent', weight='B')
    search_query = SearchQuery(value)
    return queryset.annotate(
        search=search_vector,
        rank=SearchRank(search_vector, search_query)) \
        .filter(Q(rank__gte=0.3) |
                Q(tags__slug__in=get_slugs(value))) \
        .distinct() \
        .order_by('-rank')


TIME_BLOCKS = (
    (0, 'Dopoledne'),  # [7-12]
    (1, 'Odpoledne'),  # [12-18]
    (2, 'Večer (od 18:00)'),  # [18-22]
)

REGULARITY = (
    (1, 'Jednodenní'),
    (0, 'Pravidelná'),
)


def filter_by_timeblock(queryset, _, values):
    time_blocks = []
    if '0' in values:
        morning = [i for i in range(7, 12)]
        time_blocks.extend(morning)
    if '1' in values:
        afternoon = [i for i in range(12, 19)]
        time_blocks.extend(afternoon)
    if '2' in values:
        evening = [i for i in range(19, 23)]
        time_blocks.extend(evening)
    return queryset.filter(week_schedule__hour__in=time_blocks).distinct()


class CourseFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(label='Klíčové slovo', method=filter_by_query,
                                  help_text='Při hledání více klíčových slov, či slovních spojení, oddělujte čárkami')
    is_oneoff = django_filters.ChoiceFilter(field_name='is_oneoff',
                                            choices=REGULARITY,
                                            empty_label='Bez omezení',
                                            label='Opakování')
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte', label='Minimální cena aktivity',
                                            help_text='Zvolte násobky 100')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte', label='Maximální cena aktivity')
    category = django_filters.ChoiceFilter(field_name='category',
                                           lookup_expr='exact',
                                           choices=Course.Category.choices,
                                           empty_label='Bez omezení',
                                           label='Kategorie dle zaměření')
    age_category = django_filters.ModelChoiceFilter(field_name='age_category',
                                                    lookup_expr='exact',
                                                    queryset=AgeCategory.objects.all(),
                                                    empty_label='Bez omezení',
                                                    label='Kategorie dle věku')
    week_day = django_filters.MultipleChoiceFilter(choices=WeekSchedule.WeekDay.choices,
                                                   field_name='week_schedule__day_of_week',
                                                   lookup_expr='in',  # choices get collected in a list
                                                   distinct=True,  # default
                                                   conjoined=False,  # default
                                                   label='Den v týdnu')
    time_block = django_filters.MultipleChoiceFilter(choices=TIME_BLOCKS,
                                                     method=filter_by_timeblock,
                                                     label='Část dne')
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
                                         ),
                                         Row(
                                             Column('date_from'),
                                             Column('date_to'),
                                             Column('is_oneoff')
                                         ),
                                         Div(
                                             HTML(
                                                 '<p><b>Jaká je vaše přibližná časová dostupnost?</b></p> '
                                             ),
                                             InlineCheckboxes('week_day', css_class='col-12'),
                                             InlineCheckboxes('time_block', css_class='col-12'),  # mb-3 is forced
                                             css_class='collapse border rounded px-3 pt-3 pt-0 mb-3 mb-3',
                                             id='collapseRegActivitiesFilter'
                                         ),
                                         Row(
                                             Column('category'),
                                             Column('age_category')
                                         ),
                                         )
        self.form.fields['price_min'].widget.attrs.update({'min': 0, 'max': 99999, 'step': 100})
        self.form.fields['price_max'].widget.attrs.update({'min': 0, 'max': 99999, 'step': 100})

    class Meta:
        model = Course
        fields = ['age_category', 'category']  # this works only as fallback
