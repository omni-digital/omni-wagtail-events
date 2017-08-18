# -*- coding:utf8 -*-

from __future__ import unicode_literals

from django.db import models
from django.test import TestCase
from wagtail.wagtailcore.models import Page

from wagtail_events import abstract_models


class TestAbstractPaginatedIndexPage(TestCase):
    """Tests for the AbstractPaginatedIndexPage model."""
    def setUp(self):
        self.model = abstract_models.AbstractPaginatedIndexPage

    def test_parent_class(self):
        """AbstractPaginatedIndexPage shoild inhert from Page."""
        self.assertTrue(issubclass(self.model, Page))

    def test_paginate_by(self):
        """Test AbstractPaginatedIndexPage.paginate_by field type."""
        field = self.model._meta.get_field('paginate_by')
        self.assertIsInstance(field, models.PositiveIntegerField)
        self.assertTrue(field.blank)
        self.assertTrue(field.null)


class TestAbstractEventIndexPage(TestCase):
    """Tests for the AbstractEventIndexPage model."""
    def test_parent_class(self):
        """The model should inhert from page & AbstractPaginatedIndexPage."""
        self.assertTrue(issubclass(
            abstract_models.AbstractEventIndexPage,
            abstract_models.AbstractPaginatedIndexPage
        ))


class TestAbstractEventInstance(TestCase):
    """Test fot the AbstractEventInstance model."""
    def setUp(self):
        self.model = abstract_models.AbstractEventInstance

    def test_parent_class(self):
        """AbstractEventInstance should inhert from models.Model."""
        self.assertTrue(issubclass(self.model, models.Model))

    def test_title(self):
        """Test the AbstractEventInstance.title field."""
        field = self.model._meta.get_field('title')
        self.assertIsInstance(field, models.CharField)
        self.assertFalse(field.blank)
        self.assertFalse(field.null)

    def test_start_date(self):
        """Test the AbstractEventInstance.start_date field."""
        field = self.model._meta.get_field('start_date')
        self.assertIsInstance(field, models.DateTimeField)
        self.assertFalse(field.blank)
        self.assertFalse(field.null)

    def test_end_date(self):
        """Test the AbstractEventInstance.end_date field."""
        field = self.model._meta.get_field('end_date')
        self.assertIsInstance(field, models.DateTimeField)
        self.assertTrue(field.blank)
        self.assertTrue(field.null)
