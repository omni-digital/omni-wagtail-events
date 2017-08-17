# -*- coding:utf8 -*-

from __future__ import unicode_literals

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from tests.factories import EventDetailPageFactory, EventInstanceFactory
from wagtail_events import date_filters
from wagtail_events.models import EventDetailPage, EventInstance


class TestGetAgendas(TestCase):
    """ """
    def setUp(self):
        self.now = timezone.now()
        self.detail = EventDetailPageFactory.create(parent=None)
        self.instance_one = EventInstanceFactory.create(
            event=self.detail,
            start_date=self.now,
        )

    def test_get_year_agenda(self):
        """ """
        instance_two = EventInstanceFactory.create(
            event=self.detail,
            start_date=self.now-timedelta(days=365),
        )
        response = date_filters.get_year_agenda(
            EventInstance,
            EventDetailPage.objects.all(),
            self.now,
        )

        self.assertEqual(response['scope'], 'Year')
        self.assertIn(self.instance_one, response['items'])
        self.assertNotIn(instance_two, response['items'])

    def test_get_month_agenda(self):
        """ """
        instance_two = EventInstanceFactory.create(
            event=self.detail,
            start_date=self.now-timedelta(weeks=4),
        )
        response = date_filters.get_month_agenda(
            EventInstance,
            EventDetailPage.objects.all(),
            self.now,
        )

        self.assertEqual(response['scope'], 'Month')
        self.assertIn(self.instance_one, response['items'])
        self.assertNotIn(instance_two, response['items'])

    def test_get_week_agenda(self):
        """ """
        instance_two = EventInstanceFactory.create(
            event=self.detail,
            start_date=self.now-timedelta(weeks=1),
        )
        response = date_filters.get_week_agenda(
            EventInstance,
            EventDetailPage.objects.all(),
            self.now,
        )

        self.assertEqual(response['scope'], 'Week')
        self.assertIn(self.instance_one, response['items'])
        self.assertNotIn(instance_two, response['items'])

    def test_get_day_agenda(self):
        """ """
        instance_two = EventInstanceFactory.create(
            event=self.detail,
            start_date=self.now-timedelta(days=1),
        )
        response = date_filters.get_day_agenda(
            EventInstance,
            EventDetailPage.objects.all(),
            self.now,
        )

        self.assertEqual(response['scope'], 'Day')
        self.assertIn(self.instance_one, response['items'])
        self.assertNotIn(instance_two, response['items'])
