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
