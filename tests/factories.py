# -*- coding:utf8 -*-

from __future__ import unicode_literals

import factory

from wagtail_factories import PageFactory

from wagtail_events import models


class EventDetailPageFactory(PageFactory):
    """Factory for wagtail_events.models.EventDetailPage"""
    title = factory.Sequence('Event {}'.format)
    body = factory.Sequence('Event {} information.'.format)

    class Meta(object):
        """Factory properties."""
        model = models.EventDetailPage


class EventIndexPageFactory(PageFactory):
    """Factory for wagtail_events.models.EventIndexPage"""
    title = factory.Sequence('Event List {}'.format)
    body = factory.Sequence('Event List {} information.'.format)

    class Meta(object):
        """Factory properties."""
        model = models.EventIndexPage


class EventInstanceFactory(factory.django.DjangoModelFactory):
    """Factory for wagtail_events.models.EventInstance"""
    title = factory.Sequence('Event instance {}'.format)
    body = factory.Sequence('Event instance {} information.'.format)

    class Meta(object):
        """Factory properties."""
        model = models.EventInstance
