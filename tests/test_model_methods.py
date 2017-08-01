# -*- coding:utf8 -*-

from __future__ import unicode_literals

from datetime import timedelta

from django.test import TestCase
from django.utils.timezone import now

from omni_wagtail_events.models import AgendaItems
from tests.factories import EventDetailPageFactory, EventListingPageFactory


class EventTestCase(TestCase):
    """TestCase for the events"""
    def setUp(self):
        self.time_now = now()
        self.index = EventListingPageFactory.create(parent=None)


class EventListingPageTestCase(EventTestCase):
    """Tests for the EventListingPage model's methods."""
    def test_get_day_agenda_no_data(self):
        """Queryset should contain empty data if no event."""
        data = self.index.get_day_agenda(self.time_now)

        self.assertIn('items', data)
        self.assertEqual(len(data.get('items')), 0)

    def test_get_day_agenda_non_recurring_event(self):
        """Queryset should contain non recurring events."""
        EventDetailPageFactory.create(
            parent=self.index,
            start_time=self.time_now,
            end_time=self.time_now+timedelta(hours=1),
        )
        data = self.index.get_day_agenda(self.time_now)

        self.assertIn('items', data)
        self.assertEqual(len(data.get('items')), 1)

    def test_get_day_agenda_recurring_event(self):
        """Queryset should contain recurring events."""
        EventDetailPageFactory.create(
            parent=self.index,
            start_time=self.time_now-timedelta(days=1, hours=2),
            end_time=self.time_now-timedelta(days=1, hours=1),
            repeat=1,
            period=1,
        )
        data = self.index.get_day_agenda(self.time_now)

        self.assertIn('items', data)
        self.assertEqual(len(data.get('items')), 1)

    def test_get_week_agenda_no_data(self):
        """Queryset should contain empty data if no event."""
        data = self.index.get_week_agenda(self.time_now)

        self.assertIn('items', data)
        self.assertEqual(len(data.get('items')), 0)

    def test_get_week_agenda_non_recurring_event(self):
        """Queryset should contain non recurring events."""
        EventDetailPageFactory.create(
            parent=self.index,
            start_time=self.time_now,
            end_time=self.time_now+timedelta(days=2),
        )
        data = self.index.get_week_agenda(self.time_now)

        self.assertIn('items', data)
        self.assertEqual(len(data.get('items')), 1)

    def test_get_weeek_agenda_recurring_event(self):
        """Queryset should contain recurring events."""
        EventDetailPageFactory.create(
            parent=self.index,
            start_time=self.time_now-timedelta(weeks=1, hours=2),
            end_time=self.time_now-timedelta(weeks=1, hours=1),
            repeat=1,
            period=2,
        )
        data = self.index.get_week_agenda(self.time_now)

        self.assertIn('items', data)
        self.assertEqual(len(data.get('items')), 1)

    def test_get_month_agenda_no_data(self):
        """Queryset should contain empty data if no event."""
        data = self.index.get_month_agenda(self.time_now)

        self.assertIn('items', data)
        self.assertEqual(len(data.get('items')), 0)

    def test_get_month_agenda_non_recurring_event(self):
        """Queryset should contain non recurring events."""
        EventDetailPageFactory.create(
            parent=self.index,
            start_time=self.time_now,
            end_time=self.time_now+timedelta(days=2),
        )
        data = self.index.get_month_agenda(self.time_now)

        self.assertIn('items', data)
        self.assertEqual(len(data.get('items')), 1)

    def test_get_month_agenda_recurring_event(self):
        """Queryset should contain recurring events."""
        EventDetailPageFactory.create(
            parent=self.index,
            start_time=self.time_now-timedelta(weeks=4, hours=2),
            end_time=self.time_now-timedelta(weeks=4, hours=1),
            repeat=1,
            period=3,
        )
        data = self.index.get_month_agenda(self.time_now)

        self.assertIn('items', data)
        self.assertEqual(len(data.get('items')), 1)

    def test_get_year_agenda_no_data(self):
        """Queryset should contain empty data if no event."""
        data = self.index.get_year_agenda(self.time_now)

        self.assertIn('items', data)
        self.assertEqual(len(data.get('items')), 0)

    def test_get_year_agenda_non_recurring_event(self):
        """Queryset should contain non recurring events."""
        EventDetailPageFactory.create(
            parent=self.index,
            start_time=self.time_now,
            end_time=self.time_now+timedelta(days=2),
        )
        data = self.index.get_year_agenda(self.time_now)

        self.assertIn('items', data)
        self.assertEqual(len(data.get('items')), 1)

    def test_get_year_agenda_recurring_event(self):
        """Queryset should contain recurring events."""
        EventDetailPageFactory.create(
            parent=self.index,
            start_time=self.time_now-timedelta(weeks=52, hours=2),
            end_time=self.time_now-timedelta(weeks=52, hours=1),
            repeat=1,
            period=4,
        )
        data = self.index.get_year_agenda(self.time_now)

        self.assertIn('items', data)
        self.assertEqual(len(data.get('items')), 1)


class EventDetailPageTestCase(EventTestCase):
    """Tests for the AgendaItems model"""
    def test_agenda_creation(self):
        """EventDetailPage should create a single AgendaItems instance."""
        event = EventDetailPageFactory.create(
            parent=self.index,
            start_time=self.time_now,
            end_time=self.time_now+timedelta(hours=1)
        )
        agenda_item = AgendaItems.objects.get()

        self.assertEqual(agenda_item.page, event)
        self.assertEqual(agenda_item.start_time, event.start_time)
        self.assertEqual(agenda_item.end_time, event.end_time)

    def test_recurring_agenda_creation(self):
        """EventDetailPage should recurring events if repeat is set."""
        event = EventDetailPageFactory.create(
            parent=self.index,
            start_time=self.time_now,
            end_time=self.time_now+timedelta(hours=1),
            repeat=10,  # Number of duplicates
            period=1,  # days
        )
        agenda_items = AgendaItems.objects.filter(page=event)

        self.assertEqual(agenda_items.count(), 11)  # Original instance and 10 duplicates
        for counter, item in enumerate(agenda_items):
            self.assertEqual(item.start_time, self.time_now+timedelta(days=counter))
            self.assertEqual(item.end_time, self.time_now+timedelta(days=counter, hours=1))
