# -*- coding:utf8 -*-
"""
Application model managers
"""

from __future__ import unicode_literals

from django.db import models


class AgendaItemsManager(models.Manager):

    @staticmethod
    def _get_min_time(dt):
        """
        Makes clock to 00:00:00
        :param dt: datetime
        :return: datetime
        """
        return dt.replace(hour=0, minute=0, second=0)

    def in_date_range(self, start, end):
        """
        Get event dates that appear between the start and end dates
        :return: Filtered django model queryset
        """
        start = self._get_min_time(start)
        end = self._get_min_time(end)
        return self.filter(start_time__gte=start, end_time__lte=end)

    def parent_ids_by_date(self, start, end):
        """
        Get only events that are periodically recurring
        :return: Filtered django model queryset
        """
        return self.in_date_range(start, end).values_list('page_id', flat=True)
