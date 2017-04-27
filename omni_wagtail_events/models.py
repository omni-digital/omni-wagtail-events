# -*- coding:utf8 -*-
"""

"""

from __future__ import unicode_literals

import datetime

from django.db import models

from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel, MultiFieldPanel, FieldRowPanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page


class EventListingPage(Page):
    """
    Event index page
    """
    content = RichTextField()
    paginate_by = models.IntegerField()

    content_panels = Page.content_panels + [
        FieldPanel('content'),
        FieldPanel('paginate_by'),
    ]

    subpage_types = ['EventDetailPage']

    def get_year_agenda(self):
        pass

    def get_month_agenda(self):
        pass

    def get_week_agenda(self):
        pass

    def get_day_agenda(self):
        pass

        now = datetime.datetime.utcnow().date()

        # items =

    def get_context(self, request, *args, **kwargs):
        """
        Adds child pages to the context and paginates them if pagination is required
        :param request: HttpRequest instance
        :param args: default positional args
        :param kwargs: default keyword args
        :return: Context data to use when rendering the template
        """
        context = super(EventListingPage, self).get_context(request, *args, **kwargs)

        default_period = 'week'
        time_periods = {
            'year': self.get_year_agenda,
            default_period: self.get_week_agenda,
            'month': self.get_month_agenda,
            'day': self.get_day_agenda,
        }

        period = request.GET.get('period', default_period).lower()

        if period not in time_periods.keys():
            return context

        context['items'] = time_periods[period]()

        return context


class EventDetailPage(Page):
    """
    Event details concrete model
    """

    content = RichTextField()

    # empty `repeat` field + selected `period` choice means `forever`
    repeat = models.PositiveSmallIntegerField(blank=True, null=True)

    PERIODS = (
        (1, 'days'),
        (2, 'weeks'),
        (3, 'months'),
        (4, 'years'),
    )
    period = models.PositiveSmallIntegerField(choices=PERIODS, blank=True, null=True)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)

    parent_page_types = ['EventListingPage']

    content_panels = Page.content_panels + [
        FieldPanel('content'),
        FieldRowPanel([FieldPanel('repeat'), FieldPanel('period')]),
        FieldRowPanel([FieldPanel('start_time'), FieldPanel('end_time')], 'Date of occurrence'),
    ]

    def is_recurring(self):
        """
        Check if the event is recurring
        
        :return: Boolean 
        """
        if self.period and not self.repeat:
            return True

        return False

    def is_happening_today(self, date):
        """
        Check if recurring event is happening today
        
        :param date: 
        :return: 
        """
        if not self.is_recurring() and self.start_time.date() != date:
            return False

    def create_event_dates(self):
        if self.is_recurring():
            return

        # Delete existing dates
        [c.delete() for c in self.get_children()]

        # Create new date items
        instance = EventDatePage()
        start_time = self.start_time
        end_time = self.end_time

        # self.add_child(instance=EventDatePage(
        #
        # ))

    def save(self, *args, **kwargs):
        super(EventDetailPage, self).save(*args, **kwargs)
        self.create_event_dates()


class EventDatePage(Page):
    """
    Event occurrence concrete model 
    """
    parent_page_types = ['EventDetailPage']

    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
