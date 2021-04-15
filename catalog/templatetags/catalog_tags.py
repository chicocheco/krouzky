from django import template
from django.utils.safestring import mark_safe

register = template.Library()


# pagination
@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """
    Return encoded URL parameters that are the same as the current request's parameters, only with the specified
    GET parameters added or changed.
    """
    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    return d.urlencode()


# week schedule widget
@register.simple_tag
def set_row(counter):
    """
    Break a row after every 8th column within the table and mark it.
    Choices MUST be ordered by hour (0-23) and then week days (0-6).
    """
    if counter % 7 == 0:
        return mark_safe('<tr>')
    return ''
