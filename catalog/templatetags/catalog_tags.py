from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()


# pagination
@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """
    Return encoded URL parameters that are the same as the current request's parameters,
    only with the specified GET parameters added or changed.
    """

    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    for k in [k for k, v in d.items() if not v]:  # remove empty
        del d[k]
    return d.urlencode()


# week schedule widget
@register.simple_tag
def set_row(counter, columns=7):
    """Break a table row after every Xth column within the table."""

    if counter % columns == 0:
        return mark_safe('<tr>')
    return ''


@register.simple_tag
def convert_hour_block(hour):
    return f'{str(hour).zfill(2)}:00'


@register.filter
def strip_protocol(value):
    return re.sub('https?://', '', value).strip('/')
