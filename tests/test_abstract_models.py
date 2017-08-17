# -*- coding:utf8 -*-

from __future__ import unicode_literals

from django.db import models
from django.test import TestCase
from wagtail.wagtailcore.models import Page

from wagtail_events import abstract_models


class TestAbstractPaginatedIndexPage(TestCase):
    """ """
    def setUp(self):
        self.model = abstract_models.AbstractPaginatedIndexPage

    def test_parent_class(self):
        """ """
        self.assertTrue(issubclass(self.model, Page))

    def test_paginate_by(self):
        """ """
        field = self.model._meta.get_field('paginate_by')
        self.assertIsInstance(field, models.PositiveIntegerField)
        self.assertTrue(field.blank)
        self.assertTrue(field.null)


class TestAbstractEventIndexPage(TestCase):
    """ """
    def test_parent_class(self):
        """ """
        self.assertTrue(issubclass(
            abstract_models.AbstractEventIndexPage,
            abstract_models.AbstractPaginatedIndexPage
        ))


class TestAbstractEventInstance(TestCase):
    """ """
    def setUp(self):
        self.model = abstract_models.AbstractEventInstance

    def test_parent_class(self):
        """ """
        self.assertTrue(issubclass(self.model, models.Model))

    def test_title(self):
        """ """
        field = self.model._meta.get_field('title')
        self.assertIsInstance(field, models.CharField)
        self.assertFalse(field.blank)
        self.assertFalse(field.null)

    def test_start_date(self):
        """ """
        field = self.model._meta.get_field('start_date')
        self.assertIsInstance(field, models.DateTimeField)
        self.assertFalse(field.blank)
        self.assertFalse(field.null)

    def test_end_date(self):
        """ """
        field = self.model._meta.get_field('end_date')
        self.assertIsInstance(field, models.DateTimeField)
        self.assertTrue(field.blank)
        self.assertTrue(field.null)
