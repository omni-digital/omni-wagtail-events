# -*- coding:utf8 -*-
"""
Application Model utilities
"""

from __future__ import unicode_literals

import datetime


def get_max_week_id(year):
    """
    Get max week id in year
    :param year: year
    :return: Integer
    """
    first_day = datetime.date(year, 12, 25)
    next_week = first_day + datetime.timedelta(days=7)
    return next_week.isocalendar()[1]

def get_max_day_id(year):
    """
    Get max day id in year
    :param year: year
    :return: Integer
    """
    return (datetime.date(year, 1, 1) - datetime.date(year-1, 1, 1)).days - 1

def date_to_datetime(date, time_choice='min'):
    """
    Convert date to datetime

    :param date: date to convert
    :param time_choice: max or min
    :return: datetime
    """
    choice = getattr(datetime.datetime, 'min' if time_choice == 'min' else 'max').time()
    return datetime.datetime.combine(date, choice)
