from django import template

register = template.Library()

@register.filter
def filter_by_body_type(users, body_type):
    return [u for u in users if u.body_type == body_type]

@register.filter
def filter_by_spicy(users, spicy):
    return [u for u in users if u.spicy_pref == spicy]

@register.filter
def filter_active(users, threshold):
    return [u for u in users if u.interaction_count >= threshold]

@register.filter
def filter_moderate(users, args):
    min_val, max_val = map(int, str(args).split(':'))
    return [u for u in users if min_val <= u.interaction_count < max_val]

@register.filter
def filter_low(users, threshold):
    return [u for u in users if u.interaction_count < threshold]

@register.filter
def filter_meal_type(foods, meal_type):
    return [f for f in foods if f.meal_type == meal_type]

@register.filter
def split(value, delimiter):
    return value.split(delimiter)