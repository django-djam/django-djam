from django.test import TestCase
from django.test.client import RequestFactory
from django.core.exceptions import ImproperlyConfigured
from django.conf.urls import patterns, url
from django.views.generic import View

from djam.riffs.base import Riff
from djam.riffs.tests.common import GenericURLResolver


class TestRiff(Riff):
    verbose_name = 'test riff'
    
    def get_extra_urls(self):
        return patterns('',
            url(r'^login/$',
                View.as_view(),
                name='login'),
        )

class BaseRiffTestCase(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()
        self.riff = self.get_test_riff()
        
        #TODO it would be nice if django's test case could just use this!
        self.resolver = GenericURLResolver(r'^', self.riff.get_urls())
        
        def reverse(name, *args, **kwargs):
            ret = self.resolver.reverse(name, *args, **kwargs)
            return ret
        
        self.riff.reverse = reverse
    
    def get_test_riff(self):
        return TestRiff()

    def test_riff_requires_verbose_name(self):
        self.assertRaises(ImproperlyConfigured, Riff)

    def test_get_urls(self):
        urls = self.riff.get_urls()

        purls, appname, namespace = self.riff.urls

        #self.assertEquals(urls, purls)
        self.assertEquals(self.riff.namespace, namespace)

    def test_reverse(self):
        url = self.riff.reverse('login')
        self.assertEqual('login/', url)
    
    def test_get_unauthorized_response(self):
        request = self.request_factory.get('/')
        response = self.riff.get_unauthorized_response(request)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'], '{url}?next=/'.format(url=self.riff.reverse('login')))
