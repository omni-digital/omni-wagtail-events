# -*- coding:utf8 -*-
"""
omni_wagtail_events abstract models
"""


from __future__ import unicode_literals

from datetime import timedelta

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import models
from wagtail.wagtailadmin.edit_handlers import FieldPanel, FieldRowPanel
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.models import Orderable


class AbstractEventListingPage(Page):
    paginate_by = models.PositiveIntegerField(blank=True, null=True)

    content_panels = Page.content_panels + [FieldPanel('paginate_by')]

    class Meta(object):
        """Django model meta options."""
        abstract = True

    def _paginate_queryset(self, queryset, page):
        """
        Helper method for paginating the queryset provided.

        :param queryset: Queryset of model instances to paginate
        :param page: Raw page number taken from the request dict
        :return: Queryset of child model instances
        """
        paginator = Paginator(queryset, self.paginate_by)
        try:
            queryset = paginator.page(page)
        except PageNotAnInteger:
            queryset = paginator.page(1)
        except EmptyPage:
            queryset = paginator.page(paginator.num_pages)
        return queryset, paginator


class AbstractEventDetailPage(Page):
    """ """
    PERIODS = (
        (1, 'days'),
        (2, 'weeks'),
        (3, 'months'),
        (4, 'years'),
    )
    period = models.PositiveSmallIntegerField(blank=True, choices=PERIODS, null=True)
    repeat = models.PositiveSmallIntegerField(blank=True, null=True, default=0)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldRowPanel([FieldPanel('repeat'), FieldPanel('period')]),
        FieldRowPanel(
            [FieldPanel('start_time'), FieldPanel('end_time')],
            'Date of occurrence',
        ),
    ]

    class Meta(object):
        """Django model meta options."""
        abstract = True

    def is_recurring(self):
        """
        Check if the event is recurring

        :return: Boolean
        """
        if self.period and self.repeat:
            return True

        return False

    def happens_in_date(self, check_date):
        """
        Check if the recurring event happens in a given date

        :param check_date:
        :return:
        """

        start_date = self.start_time.date()
        end_date = check_date.date()
        difference = self.get_recurring_period_in_days()

        while True:
            start_date = start_date + timedelta(days=difference)
            if start_date == end_date:
                return True
            if start_date > end_date:
                break

        return False

    def get_recurring_period_in_days(self):
        """
        Get event recurring period in days. We don't care for a now that
        there are different months and different years.

        :return: integer
        """
        if not self.is_recurring():
            return 0

        days_map = {
            1: 1,  # day
            2: 7,  # week
            3: 30,  # month
            4: 365  # year
        }
        return days_map.get(self.period)


class AbstractAgendaItems(Orderable, models.Model):
    """Associates an event page and an event date"""
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)

    panels = [FieldPanel('start_time'), FieldPanel('end_time')]

    class Meta(object):
        """Django model meta options."""
        abstract = True
