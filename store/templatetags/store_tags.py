from django import template

register = template.Library()


@register.filter
def split(value, delimiter=','):
    """Split a string by a delimiter. Usage: {{ "a,b,c"|split:"," }}"""
    return value.split(delimiter)


@register.filter
def multiply(value, arg):
    """Multiply value by arg."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''


@register.filter
def subtract(value, arg):
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return ''


@register.simple_tag
def url_replace(request, field, value):
    """Replace a single GET param, keeping the rest."""
    d = request.GET.copy()
    d[field] = value
    return d.urlencode()
