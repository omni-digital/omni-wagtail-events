# -*- coding:utf8 -*-
"""
Application model admin configuration
"""

from __future__ import unicode_literals

from django.contrib import admin
from omni_wagtail_events import models


admin.site.register([
    models.EventListingPage,
    models.EventDetailPage,
    models.AgendaItems,
])
