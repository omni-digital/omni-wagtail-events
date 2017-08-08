# -*- coding:utf8 -*-
"""
Application Model utilities
"""

from __future__ import unicode_literals

import calendar
import datetime
import re

from django.utils import timezone


_DATE_FORMAT_RE = '^([0-9]){4}\.([0-9]){2}\.([0-9]){2}$'


def date_to_datetime(date, time_choice='min'):
    """
    Convert date to datetime

    :param date: date to convert
    :param time_choice: max or min
    :return: datetime
    """
    choice = getattr(datetime.datetime, 'min' if time_choice == 'min' else 'max').time()
    return timezone.make_aware(
        datetime.datetime.combine(date, choice),
        timezone.get_current_timezone(),
    )


def add_months(date, months):
    """
    Add months to the date

    :param date:
    :param months:
    :return:
    """
    month = date.month - 1 + months
    year = int(date.year + month / 12)
    month = month % 12 + 1
    day = min(date.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


def remove_months(date, months):
    """
    Add months to the date

    :param date:
    :param months:
    :return:
    """
    month = date.month - 1 - months
    year = int(date.year + month / 12)
    month = month % 12 + 1
    day = min(date.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


def get_extra_context(context, instance, request, date_format=_DATE_FORMAT_RE):
    """
    Adds child pages to the context and paginates them if required.

    :param context: Context dictionary.
    :param instance: EventListingPage instance.
    :param request: HttpRequest instance.
    :return: Context data to use when rendering the template.
    """
    default_period = 'day'
    time_periods = {
        'year': instance.get_year_agenda,
        'week': instance.get_week_agenda,
        'month': instance.get_month_agenda,
        default_period: instance.get_day_agenda,
    }

    period = request.GET.get('scope', default_period).lower()

    if period not in time_periods.keys():
        return context

    start_date = request.GET.get('start_date', '')
    if re.match(date_format, start_date):
        date_params = [int(i) for i in start_date.split('.')]
        start_date = date_to_datetime(datetime.date(*date_params))
    else:
        start_date = timezone.now()

    agenda = time_periods[period](start_date)
    is_paginated = False
    paginator = None

    # Paginate the child nodes if paginate_by has been specified
    if instance.paginate_by:
        is_paginated = True
        agenda['items'], paginator = instance._paginate_queryset(
            agenda['items'],
            request.GET.get('page')
        )

    context.update(
        agenda=agenda,
        paginator=paginator,
        is_paginated=is_paginated
    )
    return context
