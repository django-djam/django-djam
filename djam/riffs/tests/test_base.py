from django.test import TestCase
from django.core.exceptions import ImproperlyConfigured

from djam.riffs.base import Riff


class BaseRiffTestCase(TestCase):
    def test_riff_requires_verbosename(self):
        self.assertRaises(ImproperlyConfigured, Riff)
