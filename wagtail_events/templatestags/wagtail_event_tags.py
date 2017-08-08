# -*- coding:utf8 -*-
"""
Wagtail events template tags
"""

from __future__ import unicode_literals

from django import template

try:
    import urllib.urlencode as urlencode
except ImportError:
    from urllib.parse import urlencode


register = template.Library()


@register.simple_tag(takes_context=True)
def querystring(context, *args, **kwargs):
    """
    Display all GET values (except page) encoded as url params
    :param context: template context
    :return: string|encoded params as urlstring
    """
    try:
        params = context['request'].GET.dict()
    except (KeyError, AttributeError):
        params = {}
    else:
        for value in args:
            params.pop(value, None)
        for key, value in kwargs.items():
            params[key] = value
    return urlencode(params)
