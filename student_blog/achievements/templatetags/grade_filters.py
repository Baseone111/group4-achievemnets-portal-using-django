
from django import template


register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Allows accessing dictionary items by key in a template."""
    return dictionary.get(key)

@register.filter
def get_quality_points(grade_str):
   
    grade_dict = {
        'A+': 5.0,
        'A': 5.0,
        'B+': 4.5,
        'B': 4.0,
        'C+': 3.5,
        'C':3.0,
        'D+':2.5,
        'D':2.0,
        'E+':1.5,
        'E-':1.0
    }
    return grade_dict.get(grade_str.upper(), "N/A")  # Default to N/A if unknown
