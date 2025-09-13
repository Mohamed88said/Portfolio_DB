from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter
def split(value, delimiter=','):
    """Split a string by the given delimiter"""
    if value is None:
        return []
    return [item.strip() for item in str(value).split(delimiter)]

@register.filter
def trim(value):
    """Trim whitespace from a string"""
    if value is None:
        return ''
    return str(value).strip()

@register.filter
def join(value, delimiter=', '):
    """Join a list with the given delimiter"""
    if value is None:
        return ''
    return delimiter.join(str(item) for item in value)

@register.filter
def truncatewords_html(value, arg):
    """Truncate HTML content while preserving tags"""
    if not value:
        return ''
    
    words = str(value).split()
    if len(words) <= int(arg):
        return value
    
    truncated = ' '.join(words[:int(arg)])
    return mark_safe(truncated + '...')

@register.filter
def duration(start_date, end_date=None):
    """Calculate duration between two dates"""
    from datetime import date
    
    if not start_date:
        return ""
    
    if not end_date:
        end_date = date.today()
    
    years = end_date.year - start_date.year
    months = end_date.month - start_date.month
    
    if months < 0:
        years -= 1
        months += 12
    
    if years > 0 and months > 0:
        return f"{years} an{'s' if years > 1 else ''} et {months} mois"
    elif years > 0:
        return f"{years} an{'s' if years > 1 else ''}"
    elif months > 0:
        return f"{months} mois"
    else:
        return "Moins d'un mois"

@register.simple_tag
def get_skill_percentage(proficiency):
    """Get percentage for skill proficiency"""
    percentages = {
        'beginner': 25,
        'intermediate': 50,
        'advanced': 75,
        'expert': 100,
    }
    return percentages.get(proficiency, 0)

@register.filter
def filesizeformat_custom(bytes_value):
    """Format file size in human readable format"""
    if not bytes_value:
        return "0 B"
    
    try:
        bytes_value = int(bytes_value)
    except (ValueError, TypeError):
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} TB"

@register.inclusion_tag('portfolio/includes/social_links.html')
def social_links(profile, size='normal'):
    """Render social media links"""
    return {
        'profile': profile,
        'size': size
    }

@register.inclusion_tag('portfolio/includes/skill_badge.html')
def skill_badge(skill):
    """Render skill badge with progress"""
    return {'skill': skill}