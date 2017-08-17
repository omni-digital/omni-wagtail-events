# -*- coding:utf8 -*-

from __future__ import unicode_literals

from django.core.paginator import Paginator
from django.test import RequestFactory, TestCase
from django.utils import timezone
from modelcluster.fields import ParentalKey
from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page
from wagtail_factories import SiteFactory

from tests import factories
from wagtail_events import abstract_models
from wagtail_events import models
from wagtail_events.views import EventInstanceDetailView
from wagtail_events.utils import _DATE_FORMAT_RE


class TestEventDetailPage(TestCase):
    """ """
    def setUp(self):
        self.model = models.EventDetailPage

    def test_parent_class(self):
        """ """
        self.assertTrue(issubclass(self.model, Page))
        self.assertTrue(issubclass(self.model, RoutablePageMixin))

    def test_body(self):
        """ """
        field = self.model._meta.get_field('body')

        self.assertIsInstance(field, RichTextField)
        self.assertFalse(field.blank)
        self.assertFalse(field.null)

    def test_event_view(self):
        """ """
        request = RequestFactory().get('')
        request.is_preview = False
        detail = factories.EventDetailPageFactory.create(parent=None)
        instance = factories.EventInstanceFactory.create(
            event=detail,
            start_date=timezone.now(),
        )
        response = detail.event_view(request, pk=instance.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['object'], instance)
        self.assertIsInstance(
            response.context_data['view'],
            EventInstanceDetailView,
        )


class TestEventIndexPage(TestCase):
    """ """
    def setUp(self):
        self.model = models.EventIndexPage
        self.index = factories.EventIndexPageFactory.create(parent=None)
        self.detail = factories.EventDetailPageFactory.create(
            parent=self.index
        )
        self.instance = factories.EventInstanceFactory.create(
            event=self.detail,
            start_date=timezone.now(),
        )
        self.request = RequestFactory().get('')
        self.request.is_preview = False

    def test_parent_class(self):
        """ """
        self.assertTrue(issubclass(
            self.model,
            abstract_models.AbstractEventIndexPage
        ))

    def test_body(self):
        """ """
        field = self.model._meta.get_field('body')

        self.assertIsInstance(field, RichTextField)
        self.assertFalse(field.blank)
        self.assertFalse(field.null)

    def test_get_children(self):
        """ """
        response = self.index._get_children(self.request)

        self.assertEqual(response['items'][0], self.instance)

    def test_get_children_with_time(self):
        """ """
        request = RequestFactory().get('', {
            'scope': 'year',
            'start_date': timezone.now().strftime('%Y.01.01'),
        })
        request.is_preview = False
        response = self.index._get_children(request)

        self.assertEqual(response['items'][0], self.instance)

    def test_get_children_bad_time_period(self):
        """ """
        request = RequestFactory().get('', {'scope': 'bad_scope'})
        request.is_preview = False
        response = self.index._get_children(request)

        self.assertEqual(response['items'][0], self.instance)

    def test_get_dateformat(self):
        """ """
        response = self.index.get_dateformat()

        self.assertEqual(response, _DATE_FORMAT_RE)

    def test_pagination(self):
        """ """
        factories.EventInstanceFactory.create(
            event=self.detail,
            start_date=timezone.now(),
        )
        self.index.paginate_by = 1
        self.index.save()
        response = self.index.get_context(self.request)

        self.assertIsInstance(response['paginator'], Paginator)
        self.assertTrue(response['is_paginated'])
        self.assertIn(self.instance, response['children']['items'].object_list)


class TestEventInstance(TestCase):
    """ """
    def setUp(self):
        self.model = models.EventInstance

    def test_parent_class(self):
        """ """
        self.assertTrue(issubclass(
            self.model,
            abstract_models.AbstractEventInstance
        ))

    def test_body(self):
        """ """
        field = self.model._meta.get_field('body')

        self.assertIsInstance(field, RichTextField)
        self.assertFalse(field.blank)
        self.assertFalse(field.null)

    def test_event(self):
        """ """
        field = self.model._meta.get_field('event')

        self.assertIsInstance(field, ParentalKey)
        self.assertFalse(field.blank)
        self.assertFalse(field.null)

    def test_url(self):
        """ """
        index = factories.EventIndexPageFactory.create(parent=None)
        SiteFactory.create(root_page=index)
        detail = factories.EventDetailPageFactory.create(parent=index)
        instance = factories.EventInstanceFactory.create(
            event=detail,
            start_date=timezone.now(),
        )
        self.assertEqual(instance.url, '{}{}/'.format(detail.url, instance.pk))
