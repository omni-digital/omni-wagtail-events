# -*- coding:utf8 -*-
"""
Application models
"""


from __future__ import unicode_literals

import re
import datetime
from datetime import timedelta

from isoweek import Week

from django.db import models
from django.utils.timezone import now

from modelcluster.fields import ParentalKey
from wagtail.wagtailadmin.edit_handlers import FieldPanel, FieldRowPanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Orderable, Page

from omni_wagtail_events import utils
from omni_wagtail_events import managers


_DATE_FORMAT_RE = '^([0-9]){4}\.([0-9]){2}\.([0-9]){2}$'


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

    @staticmethod
    def get_period_items(start_date, end_date):
        """
        Get list of matching events (both - recurring and single time)
        
        :param start_date: period start date
        :type start_date: datetime
        :param end_date: period end date
        :type end_date: datetime
        :return: filtered queryset
        """
        return AgendaItems.objects.in_date_range(start_date, end_date)

    def get_year_agenda(self, start_date):
        """
        Get list of events that will occur in the given year
        
        :param start_date: period start_date
        :type start_date: datetime.datetime()
        :return: data dictionary
        """

        start_date = datetime.datetime(start_date.year, 1, 1)
        end_date = utils.add_months(start_date, 12)

        return {
            'start_date': start_date,
            'end_date': end_date,
            'scope': 'Year',
            'items': self.get_period_items(start_date, utils.date_to_datetime(end_date, 'max')),
            'next_date': utils.date_to_datetime(utils.add_months(start_date.date(), 12)),
            'previous_date': utils.date_to_datetime(utils.remove_months(start_date.date(), 12)),
        }

    def get_month_agenda(self, start_date):
        """
        Get list of events that will occur in the given week
        
        :param start_date: period start_date
        :type start_date: datetime.datetime()
        :return: data dictionary
        """
        start_date = datetime.datetime(start_date.year, start_date.month, 1)
        end_date = utils.date_to_datetime(utils.add_months(start_date.date(), 1), 'max')
        return {
            'start_date': start_date,
            'end_date': end_date,
            'scope': 'Month',
            'items': self.get_period_items(start_date, end_date),
            'next_date': utils.date_to_datetime(utils.add_months(start_date.date(), 1)),
            'previous_date': utils.date_to_datetime(utils.remove_months(start_date.date(), 1)),
        }

    def get_week_agenda(self, start_date):
        """
        Get list of events that will occur in the given week
        
        :param start_date: period start_date
        :type start_date: datetime.datetime()
        :return: data dictionary
        """
        period = Week(start_date.year, start_date.date().isocalendar()[1])
        end_date = utils.date_to_datetime(period.sunday(), 'max')
        start_date = utils.date_to_datetime(period.monday())
        return {
            'start_date': start_date,
            'end_date': end_date,
            'scope': 'Week',
            'items': self.get_period_items(start_date, end_date),
            'next_date': start_date + timedelta(days=7),
            'previous_date': start_date + timedelta(days=-7),
        }

    def get_day_agenda(self, start_date):
        """
        Get list of events that will occur in the given date
        
        :param start_date: period start_date
        :type start_date: datetime.datetime()
        :return: data dictionary
        """
        next_date = start_date + timedelta(days=1)
        return {
            'start_date': start_date,
            'end_date': utils.date_to_datetime(start_date.date(), 'max'),
            'scope': 'Day',
            'items': self.get_period_items(start_date, next_date),
            'next_date': next_date,
            'previous_date': start_date + timedelta(days=-1),
        }

    def get_context(self, request, *args, **kwargs):
        """
        Adds child pages to the context and paginates them if pagination is required
        :param request: HttpRequest instance
        :param args: default positional args
        :param kwargs: default keyword args
        :return: Context data to use when rendering the template
        """
        context = super(EventListingPage, self).get_context(request, *args, **kwargs)

        default_period = 'day'
        time_periods = {
            'year': self.get_year_agenda,
            'week': self.get_week_agenda,
            'month': self.get_month_agenda,
            default_period: self.get_day_agenda,
        }

        period = request.GET.get('scope', default_period).lower()

        if period not in time_periods.keys():
            return context

        start_date = request.GET.get('start_date', '')
        if re.match(_DATE_FORMAT_RE, start_date):
            date_params = [int(i) for i in start_date.split('.')]
            start_date = utils.date_to_datetime(datetime.date(*date_params))
        else:
            start_date = now()

        context['agenda'] = time_periods[period](start_date)

        return context


class EventDetailPage(Page):
    """
    Event details concrete model
    """

    content = RichTextField()

    repeat = models.PositiveSmallIntegerField(blank=True, null=True, default=0)

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
        Get event recurring period in days. We don't care for a now that there are different 
        months and different years
        
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

        return self.repeat * days_map.get(self.period)

    def create_agenda_items(self):
        """
        Create corresponding `AgendaItems` object.
        """
        self.refresh_from_db()

        for item in self.event_dates.all():
            if item.id:
                item.delete()

        self.event_dates.create(
            start_time=self.start_time,
            end_time=self.end_time,
            page=self,
        )

        if self.is_recurring():
            period = self.get_recurring_period_in_days()
            delta = timedelta(days=period)
            start_time = self.start_time
            end_time = self.end_time
            for i in range(0, self.repeat):
                instance = self.event_dates.create(start_time=start_time, end_time=end_time, page=self)
                instance.save()
                start_time += delta
                end_time += delta

    def save(self, *args, **kwargs):
        """
        Model `save()` method.
        
        :param args: default args
        :param kwargs: default kwargs
        :return: instance of the saved object
        """
        instance = super(EventDetailPage, self).save(*args, **kwargs)
        self.create_agenda_items()
        return instance


class AgendaItems(Orderable, models.Model):
    """
    Associates an event page and an event date
    """
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)

    page = ParentalKey(EventDetailPage, related_name='event_dates')

    objects = managers.AgendaItemsManager()

    panels = [
        FieldPanel('start_time'),
        FieldPanel('end_time')
    ]
