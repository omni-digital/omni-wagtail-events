# -*- coding:utf8 -*-
"""

"""

from __future__ import unicode_literals

from datetime import timedelta

from django.test import TestCase
from django.utils.timezone import now
from wagtail.wagtailcore.models import Page

from omni_wagtail_events.models import EventListingPage, EventDetailPage, AgendaItems


class EventTestCaseStub(TestCase):
    """
    Testing stub for temporal content
    """
    def setUp(self):
        super(EventTestCaseStub, self).setUp()
        self.home_page = Page.add_root(
            title='root',
            live=True,
            slug='root',
            path='/',
        )

        self.listing_page_1 = self.home_page.add_child(
            instance=EventListingPage(
                title='event-listing-1',
                slug='event-listing-1',
                content='<p>This is the event listing page #1</p>',
                paginate_by=2,
                live=True
            )
        )

        self.listing_page_2 = self.home_page.add_child(
            instance=EventListingPage(
                title='event-listing-2',
                slug='event-listing-2',
                content='<p>This is the event listing page #2</p>',
                paginate_by=2,
                live=True
            )
        )

        self.event_1 = self.listing_page_1.add_child(
            instance=EventDetailPage(
                title='event-details-1',
                slug='event-listing-1',
                content='<p>This is the event details page #1</p>',
                start_time=now(),
                live=True
            )
        )

        self.event_2 = self.listing_page_1.add_child(
            instance=EventDetailPage(
                title='event-details-2',
                slug='event-listing-2',
                content='<p>This is the event details page #1</p>',
                live=True,
                start_time=now()
            )
        )

class EventListingPageTestCase(EventTestCaseStub):

    def test_get_day_agenda_no_data(self):
        """
        Queryset should contain empty data if no event
        """
        data = self.listing_page_1.get_day_agenda(day=now())
        self.assertIn('items', data)
        self.assertEqual(len(data.get('items')), 0)

    def test_get_day_agenda_non_recurring_event(self):
        """
        Queryset should contain non recurring events
        """
        self.event_1.start_time = now()
        self.event_1.end_time = now() + timedelta(hours=2)
        self.event_1.save()

        data = self.listing_page_1.get_day_agenda(day=now())
        self.assertIn('items', data)
        self.assertEqual(len(data.get('items')), 1)

    def test_get_day_agenda_recurring_event(self):
        """
        Queryset should contain recurring events
        """
        self.event_1.start_time = now() + timedelta(weeks=-10)
        self.event_1.end_time = now() + timedelta(weeks=-10) + timedelta(hours=2)
        self.event_1.repeat = 1
        self.event_1.period = 1
        self.event_1.save()

        data = self.listing_page_1.get_day_agenda()
        self.assertIn('items', data)
        self.assertEqual(len(data.get('items')), 0)

    def test_get_week_agenda_no_data(self):
        """
        Queryset should contain empty data if no event
        """
        data = self.listing_page_1.get_week_agenda()
        self.assertIn('items', data)
        self.assertEqual(len(data.get('items')), 0)

    def test_get_week_agenda_non_recurring_event(self):
        """
        Queryset should contain non recurring events
        """
        self.event_1.start_time = now()
        self.event_1.end_time = now() + timedelta(hours=2)
        self.event_1.save()

        data = self.listing_page_1.get_week_agenda()
        self.assertIn('items', data)
        self.assertEqual(len(data.get('items')), 1)

class AgendaItemsTestCase(EventTestCaseStub):

    def test_event_date_page_creation(self):
        """
        Should have corresponding `EventDatePage` record
        """
        repeat_times = 10
        time_base = now()
        obj = self.event_1
        obj.repeat = repeat_times
        obj.period = 1
        obj.start_time = time_base
        obj.end_time = time_base + timedelta(hours=4)
        obj.save()

        obj.refresh_from_db()

        children = AgendaItems.objects.filter(page=obj)
        child = children[0]

        self.assertEqual(repeat_times, len(children))
        self.assertEqual(obj.start_time, child.start_time)
        self.assertEqual(obj.end_time, child.end_time)

