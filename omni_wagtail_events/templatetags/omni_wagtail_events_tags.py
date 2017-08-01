# -*- coding:utf8 -*-
"""
Application template tags
"""

from __future__ import unicode_literals

from django import template

try:
    import urllib.urlencode as urlencode
except ImportError:
    from urllib.parse import urlencode


register = template.Library()


def _patch(context, key, data):
    """
    Patch the GET value

    :param context: template context dict
    :param key: item name
    :param data: item value
    :return: patched url params
    """
    getvars = dict(context['request'].GET)
    getvars[key] = [data]
    return '?{0}'.format(urlencode(getvars, doseq=True))


@register.simple_tag(takes_context=True)
def patch_start_date(context, date):
    """
    Prepare `start_date` url for agenda

    :param context: template context dict
    :param date: start_date
    :return:
    """
    return _patch(context, 'start_date', date.strftime('%Y.%m.%d'))


@register.simple_tag(takes_context=True)
def patch_scope(context, scope):
    """
    Prepare scope for agenda

    :param context:
    :param scope:
    :return:
    """
    return _patch(context, 'scope', scope)


@register.simple_tag(takes_context=True)
def patch_page(context, page):
    """
    Prepare next_url for agenda

    :param context:
    :param scope:
    :return:
    """
    return _patch(context, 'page', page)
