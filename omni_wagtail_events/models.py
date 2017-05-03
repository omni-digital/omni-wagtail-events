# -*- coding:utf8 -*-
"""
Application models
"""


from __future__ import unicode_literals

import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from isoweek import Week

from django.db import models
from django.utils.timezone import now

from wagtail.wagtailadmin.edit_handlers import FieldPanel, FieldRowPanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page, PageManager

from omni_wagtail_events import utils


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

        return EventDetailPage.objects.filter(
            models.Q(id__in=EventDatePage.objects.parent_ids_by_date(start_date, end_date)) |
            models.Q(id__in=EventDetailPage.objects.recurring_events().values_list('id', flat=True)))

    def get_year_agenda(self, year=None):
        """
        Get list of events that will occur in the given year
        
        :param year: period year
        :return: data dictionary
        """
        moment = now()
        year = year or moment.year

        start_date = datetime.datetime(year, 1, 1)
        end_date = datetime.datetime(year, 12, 1) + relativedelta(day=31)

        return {
            'items': self.get_period_items(utils.date_to_datetime(start_date), utils.date_to_datetime(end_date, 'max'))
        }

    def get_month_agenda(self, year=None, month=None):
        """
        Get list of events that will occur in the given week
        
        :param year: period year
        :type year: integer
        :param month: period month
        :type month: integer
        :return: data dictionary
        """

        moment = now()
        year = year or moment.year
        month = month or moment.month

        start_date = datetime.datetime(year, month, 1)
        end_date = start_date + relativedelta(day=31)

        return {
            'items': self.get_period_items(utils.date_to_datetime(start_date), utils.date_to_datetime(end_date, 'max'))
        }

    def get_week_agenda(self, year=None, week=None):
        """
        Get list of events that will occur in the given week
        
        :param year: period year
        :type year: integer
        :param week: period week
        :type week: integer
        :return: data dictionary
        """
        moment = now()
        year = year or moment.year
        week = week or moment.date().isocalendar()[1]

        if week > utils.get_max_week_id(year) or year < 1 or week < 1:
            return {'items': []}

        period = Week(year, week)
        return {
            'items': self.get_period_items(utils.date_to_datetime(period.monday()),
                                           utils.date_to_datetime(period.sunday(), 'max'))
        }


    def get_day_agenda(self, year=None, day=None):
        """
        Get list of events that will occur in the given date
        
        :param year: period year
        :type year: integer
        :param day: period day
        :type day: integer
        :return: data dictionary
        """

        moment = now()
        year = year or moment.year
        day = day or moment.timetuple().tm_yday

        if day > utils.get_max_day_id(year) or year < 1 or day < 1:
            return {'items': []}

        day = datetime.datetime(year, 1, 1) + datetime.timedelta(day - 1)

        return {
            'items': self.get_period_items(day, day + timedelta(days=1))
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

class EventDetailPageManager(PageManager):

    def recurring_events(self):
        """
        Get only events that are periodically recurring
        :return: Filtered django model queryset
        """
        return (self.get_queryset()
                    .filter(period__isnull=False)
                    .filter(repeat__isnull=True))


class EventDetailPage(Page):
    """
    Event details concrete model
    """

    objects = EventDetailPageManager()

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
    subpage_types = ['EventDatePage']

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

    def happens_in_period(self, period_dates):

        result = []
        for date in period_dates:
            happens = self.happens_in_date(date)
            if happens:
                result.append(date, self)
            else:
                result.append(date, False)

        return result


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

    def is_happening_today(self, today):
        """
        Check if recurring event is happening today
        
        :param today: datetime
        :return: boolean
        """
        if not self.is_recurring() and self.start_time.date() != today:
            return False

    def create_event_date(self):
        """
        Create corresponding `EventDatePage` model.
        """
        if self.is_recurring():
            return

        # Delete existing dates
        self.get_children().delete()

        self.refresh_from_db()

        return self.add_child(instance=EventDatePage(
            title='{0}: {1}'.format(str(self.start_time.date()), self.title),
            start_time=self.start_time,
            end_time=self.end_time,
        ))

    def save(self, *args, **kwargs):
        super(EventDetailPage, self).save(*args, **kwargs)
        self.create_event_date()


class EventDatePageManager(PageManager):

    def parent_ids_by_date(self, start, end):
        """
        Get only events that are periodically recurring
        :return: Filtered django model queryset
        """
        items = self.get_queryset().filter(start_time__gte=start, end_time__lte=end)
        return [c.get_parent().id for c in items]

class EventDatePage(Page):
    """
    Event occurrence concrete model 
    """
    objects = EventDatePageManager()
    parent_page_types = ['EventDetailPage']

    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
