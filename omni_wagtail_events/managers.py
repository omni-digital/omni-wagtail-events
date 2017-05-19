# -*- coding:utf8 -*-
"""
Application model managers
"""

from __future__ import unicode_literals

from django.db import models


class AgendaItemsManager(models.Manager):

    def in_date_range(self, start, end):
        """
        Get event dates that appear between the start and end dates

        :return: Filtered django model queryset
        """
        return self.get_queryset().filter(start_time__gte=start, end_time__lte=end)

    def parent_ids_by_date(self, start, end):
        """
        Get only events that are periodically recurring
        :return: Filtered django model queryset
        """
        return self.in_date_range(start, end).values_list('page_id', flat=True)
