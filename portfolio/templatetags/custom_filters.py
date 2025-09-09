from django import template

register = template.Library()

@register.filter
def split(value, delimiter=','):
    """Split a string by the given delimiter"""
    if value is None:
        return []
    return [item.strip() for item in value.split(delimiter)]

@register.filter
def trim(value):
    """Trim whitespace from a string"""
    if value is None:
        return ''
    return value.strip()

@register.filter
def join(value, delimiter=', '):
    """Join a list with the given delimiter"""
    if value is None:
        return ''
    return delimiter.join(value)