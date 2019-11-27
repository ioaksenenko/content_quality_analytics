import json

from django import template


register = template.Library()


@register.filter
def index(some_list, i):
    try:
        return some_list[int(i)]
    except IndexError:
        return None


@register.filter
def json_field(string, name):
    res = json.loads(string)
    return res[name]


@register.filter
def from_json(string):
    return json.loads(string)


@register.filter
def get(dictionary, key):
    res = dictionary[key] if key in dictionary else 'scales'
    return res


@register.filter
def next_element(list_iter):
    return next(list_iter)


@register.filter
def get_list_iter(some_list):
    some_list = iter(some_list)
    return some_list
