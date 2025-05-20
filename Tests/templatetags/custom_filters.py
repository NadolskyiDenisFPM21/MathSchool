from django import template
register = template.Library()

@register.filter
def index(sequence, i):
    try:
        return sequence[int(i)]
    except:
        return ''

@register.filter
def pair_to_text(pair, items):
    try:
        return items[pair-1]
    except (IndexError, TypeError):
        return ''