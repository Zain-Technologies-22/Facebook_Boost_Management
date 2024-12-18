from django import template
register = template.Library()

@register.filter
def abs_filter(value):
    return abs(value)