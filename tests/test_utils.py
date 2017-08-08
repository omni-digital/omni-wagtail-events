# -*- coding:utf8 -*-
"""
Application utility unittests
"""

from __future__ import unicode_literals

from django.test import RequestFactory, TestCase

from omni_wagtail_events import utils
from tests.factories import EventDetailPageFactory, EventListingPageFactory


class TestGetExtraContext(TestCase):
    """ """
    def setUp(self):
        self.index = EventListingPageFactory.create(parent=None)
        self.request = RequestFactory()

    def test_get_extra_context_no_agenda_no_pagination(self):
        """ """
        self.request.GET = {}
        response = utils.get_extra_context({}, self.index, self.request)

        self.assertFalse(response['is_paginated'])
        self.assertFalse(response['paginator'])
