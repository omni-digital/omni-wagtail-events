# -*- coding:utf8 -*-
"""
Application models
"""

from __future__ import unicode_literals

import re

from datetime import date, datetime, timedelta
from isoweek import Week

from django.utils import timezone
from modelcluster.fields import ParentalKey
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.fields import RichTextField

from omni_wagtail_events import abstract_models as abstracts
from omni_wagtail_events import utils
from omni_wagtail_events import managers


_DATE_FORMAT_RE = '^([0-9]){4}\.([0-9]){2}\.([0-9]){2}$'


class EventListingPage(abstracts.AbstractEventListingPage):
    """
    Event index page
    """
    content = RichTextField()

    content_panels = abstracts.AbstractEventListingPage.content_panels + [
        FieldPanel('content'),
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

        start_date = datetime(start_date.year, 1, 1)
        end_date = utils.add_months(start_date, 12)

        return {
            'start_date': start_date,
            'end_date': end_date,
            'scope': 'Year',
            'items': self.get_period_items(
                start_date,
                utils.date_to_datetime(end_date, 'max')
            ),
            'next_date': utils.date_to_datetime(
                utils.add_months(start_date.date(), 12)
            ),
            'previous_date': utils.date_to_datetime(
                utils.remove_months(start_date.date(), 12)
            ),
        }

    def get_month_agenda(self, start_date):
        """
        Get list of events that will occur in the given week

        :param start_date: period start_date
        :type start_date: datetime.datetime()
        :return: data dictionary
        """
        start_date = datetime(start_date.year, start_date.month, 1)
        end_date = utils.date_to_datetime(
            utils.add_months(start_date.date(), 1),
            'max'
        )
        return {
            'start_date': start_date,
            'end_date': end_date,
            'scope': 'Month',
            'items': self.get_period_items(start_date, end_date),
            'next_date': utils.date_to_datetime(
                utils.add_months(start_date.date(), 1)
            ),
            'previous_date': utils.date_to_datetime(
                utils.remove_months(start_date.date(), 1)
            ),
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
        Adds child pages to the context and paginates them if required.

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
            start_date = utils.date_to_datetime(date(*date_params))
        else:
            start_date = timezone.now()

        context['agenda'] = time_periods[period](start_date)
        """
        is_paginated = False
        paginator = None

        # Paginate the child nodes if paginate_by has been specified
        if self.paginate_by:
            is_paginated = True
            queryset, paginator = self._paginate_queryset(
                queryset,
                request.GET.get('page')
            )

        context.update(
            queryset=queryset,
            paginator=paginator,
            is_paginated=is_paginated
        )
        """
        return context


class EventDetailPage(abstracts.AbstractEventDetailPage):
    """Event details concrete model."""
    content = RichTextField()

    parent_page_types = ['EventListingPage']

    content_panels = abstracts.AbstractEventDetailPage.content_panels + [
        FieldPanel('content'),
    ]

    def create_agenda_items(self):
        """Create corresponding `AgendaItems` object."""
        self.refresh_from_db()

        for item in self.event_dates.all():
            if item.pk:
                item.delete()

        self.event_dates.add(AgendaItems.objects.create(
            start_time=self.start_time,
            end_time=self.end_time,
            page=self,
        ))

        if self.is_recurring():
            period = self.get_recurring_period_in_days()
            delta = timedelta(days=period)
            start_time = self.start_time
            end_time = self.end_time
            for i in range(0, self.repeat):
                start_time += delta
                end_time += delta
                self.event_dates.add(AgendaItems.objects.create(
                    start_time=start_time,
                    end_time=end_time,
                    page=self,
                ))

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


class AgendaItems(abstracts.AbstractAgendaItems):
    """Associates an event page and an event date."""
    page = ParentalKey(EventDetailPage, related_name='event_dates')
    objects = managers.AgendaItemsManager()
