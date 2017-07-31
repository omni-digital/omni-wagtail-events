# -*- coding:utf8 -*-
"""
Application model test case
"""

from __future__ import unicode_literals

from django.db import models
from django.test import TestCase

from wagtail.wagtailcore.fields import RichTextField
from omni_wagtail_events.models import EventListingPage, EventDetailPage


class EventListingPageModelFieldTestCase(TestCase):
    """
    Testing omni_wagtail_events.models.EventListingPage
    """
    model = EventListingPage

    def test_content_field(self):
        """
        The model should have a `content` field
        """
        field = self.model._meta.get_field('content')
        self.assertIsInstance(field, RichTextField)
        self.assertFalse(field.blank)
        self.assertFalse(field.null)

    def test_paginate_by_field(self):
        """
        The model should have a `paginate_by` field
        """
        field = self.model._meta.get_field('paginate_by')
        self.assertIsInstance(field, models.IntegerField)
        self.assertFalse(field.blank)
        self.assertFalse(field.null)

    def test_subpage_types(self):
        """
        The model should have EventDetailPage in allowed subpage types
        """
        self.assertIn('EventDetailPage', self.model.subpage_types)


class EventDetailPageModelFieldTestCase(TestCase):
    """
    Testing omni_wagtail_events.models.EventDetailPage
    """
    model = EventDetailPage

    def test_content_field(self):
        """
        The model should have a `content` field
        """
        field = self.model._meta.get_field('content')
        self.assertIsInstance(field, RichTextField)
        self.assertFalse(field.blank)
        self.assertFalse(field.null)

    def test_repeat_field(self):
        """
        The model should have a `repeat` field
        """
        field = self.model._meta.get_field('repeat')
        self.assertIsInstance(field, models.PositiveSmallIntegerField)
        self.assertTrue(field.blank)
        self.assertTrue(field.null)

    def test_period_field(self):
        """
        The model should have a `period` field
        """
        field = self.model._meta.get_field('period')
        self.assertIsInstance(field, models.PositiveSmallIntegerField)
        self.assertEqual(field.choices, self.model.PERIODS)
        self.assertTrue(field.blank)
        self.assertTrue(field.null)

    def test_start_time_field(self):
        """
        The model should have a `start_time` field
        """
        field = self.model._meta.get_field('start_time')
        self.assertIsInstance(field, models.DateTimeField)
        self.assertFalse(field.blank)
        self.assertFalse(field.null)

    def test_end_time_field(self):
        """
        The model should have a `end_time` field
        """
        field = self.model._meta.get_field('end_time')
        self.assertIsInstance(field, models.DateTimeField)
        self.assertTrue(field.blank)
        self.assertTrue(field.null)

    def test_parent_page_types(self):
        """
        The model should have EventListingPage in allowed parent page types
        """
        self.assertIn('EventListingPage', self.model.parent_page_types)
