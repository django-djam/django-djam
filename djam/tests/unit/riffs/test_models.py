from __future__ import unicode_literals

from django.test import TestCase
from django.test.client import RequestFactory
from django.core.exceptions import ImproperlyConfigured
from django.conf.urls import patterns, url
from django.views.generic import View
from django.contrib.contenttypes.models import ContentType

from djam.riffs.models import ModelRiff
from djam.tests.common import GenericURLResolver


class TestRiff(ModelRiff):
    model = ContentType

class ModelRiffTestCase(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()
        self.riff = self.get_riff()
        
        #TODO it would be nice if django's test case could just use this!
        self.resolver = GenericURLResolver(r'^', self.riff.get_urls())
        
        def reverse(name, *args, **kwargs):
            ret = self.resolver.reverse(name, *args, **kwargs)
            return ret
        
        self.riff.reverse = reverse
    
    def get_riff(self):
        return TestRiff()

    def test_get_urls(self):
        urls = self.riff.get_urls()
    
    def get_form_class(self):
        form_cls = self.riff.get_form_class()
        self.assertEqual(form_cls._meta.model, ContentType)
