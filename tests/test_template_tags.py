# -*- coding:utf8 -*-

from __future__ import unicode_literals

from django.test import RequestFactory, TestCase
from django.utils import timezone

from wagtail_events.templatetags import wagtail_events_tags


class TestQueryString(TestCase):
    """ """
    def test_no_querystring(self):
        request = RequestFactory().get('')
        context = {'request': request}
        response = wagtail_events_tags.querystring(context)

        self.assertEqual(response, '')

    def test_querystring_existing(self):
        request = RequestFactory().get('', {'scope': 'year'})
        context = {'request': request}
        response = wagtail_events_tags.querystring(context, scope='year')

        self.assertEqual(response, 'scope=year')

    def test_querystring(self):
        request = RequestFactory().get('', {'scope': 'day'})
        context = {'request': request}
        response = wagtail_events_tags.querystring(
            context,
            'scope',
            scope='year'
        )

        self.assertEqual(response, 'scope=year')


class TestPatch(TestCase):
    """ """
    def test_patch(self):
        request = RequestFactory().get('')
        context = {'request': request}
        response = wagtail_events_tags._patch(context, 'foo', 'bar')

        self.assertEqual(response, '?foo=bar')


class TestPatchScope(TestCase):
    """ """
    def test_patch_scope(self):
        request = RequestFactory().get('')
        context = {'request': request}
        response = wagtail_events_tags.patch_scope(context, 'foo')

        self.assertEqual(response, '?scope=foo')


class TestStartDate(TestCase):
    """ """
    def test_patch_start_date(self):
        request = RequestFactory().get('')
        context = {'request': request}
        time = timezone.now()
        response = wagtail_events_tags.patch_start_date(context, time)

        self.assertEqual(
            response,
            '?start_date={}'.format(time.strftime('%Y.%m.%d')),
        )
