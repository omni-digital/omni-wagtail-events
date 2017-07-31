# -*- coding:utf8 -*-
"""
Application utility unittests
"""

from __future__ import unicode_literals


from django.test import TestCase

from omni_wagtail_events import utils


class GetMaxWeekIdTestCase(TestCase):
    """
    Testing omni_wagtail_events.utils.get_max_week_id
    """
    def test_normal_response(self):
        """
        Should return valid max week ID
        """
        self.assertEqual(49, utils.get_max_week_id(2011))
        self.assertEqual(49, utils.get_max_week_id(2012))
        self.assertEqual(49, utils.get_max_week_id(2017))
