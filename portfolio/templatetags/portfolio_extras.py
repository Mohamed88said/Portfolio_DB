from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter
def split(value, delimiter=','):
    """Split a string by delimiter"""
    if value:
        return value.split(delimiter)
    return []

@register.filter
def trim(value):
    """Remove whitespace from string"""
    if value:
        return value.strip()
    return value

@register.filter
def markdown_to_html(value):
    """Convert basic markdown to HTML"""
    if not value:
        return value
    
    # Convert **bold** to <strong>
    value = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', value)
    
    # Convert *italic* to <em>
    value = re.sub(r'\*(.*?)\*', r'<em>\1</em>', value)
    
    # Convert [link](url) to <a>
    value = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', value)
    
    # Convert line breaks
    value = value.replace('\n', '<br>')
    
    return mark_safe(value)

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