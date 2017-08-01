# -*- coding:utf8 -*-
"""
Test factories.
"""

from __future__ import unicode_literals

import factory

from wagtail_factories import PageFactory

from omni_wagtail_events.models import EventDetailPage, EventListingPage


class EventDetailPageFactory(PageFactory):
    title = factory.sequence('Event Page {}'.format)
    content = factory.sequence('Event detail {} content'.format)

    class Meta:
        model = EventDetailPage


class EventListingPageFactory(PageFactory):
    title = factory.sequence('Event Listing {}'.format)
    content = factory.sequence('Event listing {} content'.format)

    class Meta:
        model = EventListingPage
