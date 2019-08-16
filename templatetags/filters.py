from django import template


register = template.Library()


@register.filter
def index(some_list, i):
    try:
        return some_list[int(i)]
    except IndexError:
        return None
