# -*- coding:utf8 -*-
"""
wagtail_events models.
"""

from __future__ import unicode_literals

import datetime
import re

from django.utils import timezone
from modelcluster.fields import ParentalKey
from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin, route
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page

from wagtail_events import abstract_models as abstracts
from wagtail_events import date_filters
from wagtail_events import utils


class EventDetailPage(RoutablePageMixin, Page):
    """ """
    body = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('body'),
        InlinePanel('events', label='Event Dates'),
    ]

    @route(r'(?P<pk>\d+)/$', name='event_detail')
    def event_view(self, request, *args, **kwargs):
        from wagtail_events.views import EventInstanceDetailView
        return EventInstanceDetailView.as_view()(request, *args, **kwargs)

    parent_page_types = ['wagtail_events.EventIndexPage']
    subpage_types = []


class EventInstance(abstracts.AbstractEventInstance):
    """ """
    body = RichTextField()
    event = ParentalKey(EventDetailPage, related_name='events')

    @property
    def url(self):
        """Returns the full url of the object."""
        url = self.event.reverse_subpage('event_detail', kwargs={'pk': self.pk})
        return self.event.url + url

    panels = abstracts.AbstractEventInstance.panels + [FieldPanel('body')]


class EventIndexPage(abstracts.AbstractEventIndexPage):
    """ """
    body = RichTextField()

    content_panels = abstracts.AbstractPaginatedIndexPage.content_panels + [
        FieldPanel('body'),
    ]

    def _get_children(self, request):
        """
        Gets the EventInstances related to the EventDetailPages.

        :param request: django request
        :return: Queryset of child model instances
        """
        qs = super(EventIndexPage, self)._get_children(request)

        default_period = 'day'
        time_periods = {
            'year': date_filters.get_year_agenda,
            'week': date_filters.get_week_agenda,
            'month': date_filters.get_month_agenda,
            default_period: date_filters.get_day_agenda,
        }
        period = request.GET.get('scope', default_period).lower()

        if period not in time_periods.keys():
            return {'items': EventInstance.objects.filter(event__in=qs)}

        start_date = request.GET.get('start_date', '')
        if re.match(self.get_dateformat(), start_date):
            date_params = [int(i) for i in start_date.split('.')]
            start_date = utils.date_to_datetime(datetime.date(*date_params))
        else:
            start_date = timezone.now().replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )

        return time_periods[period](EventInstance, qs, start_date)

    subpage_types = ['wagtail_events.EventDetailPage']
