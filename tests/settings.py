# -*- coding: utf-8 -*-
"""
Django settings for the project.
"""

from __future__ import absolute_import, unicode_literals

import django


SECRET_KEY = 'SuperSecret'

INSTALLED_APPS = [
    'omni_wagtail_events',

    'modelcluster',
    'taggit',

    'wagtail.wagtailcore',
    'wagtail.wagtailimages',
    'wagtail.wagtailusers',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
]

if django.VERSION >= (1, 10):
    MIDDLEWARE = ()
else:
    MIDDLEWARE_CLASSES = ()

DATABASES = {
    'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
