from django.test import TestCase
from django.test.client import RequestFactory
from django.core.exceptions import ImproperlyConfigured
from django.conf.urls import patterns, url
from django.views.generic import View
from django.contrib.contenttypes.models import ContentType
from django import forms

from djam.riffs.models import ModelRiff
from djam.views.models import ModelListView, ModelDetailView, ModelDeleteView, ModelHistoryView
from djam.tests.common import SuperUserRequestFactory


class TestRiff(ModelRiff):
    model = ContentType

class BaseModelViewTestCase(TestCase):
    def setUp(self):
        self.request_factory = SuperUserRequestFactory()
        self.riff = self.get_riff()
        
        class form_class(forms.ModelForm):
            class Meta:
                model = ContentType
        
        self.form_class = form_class

    def get_riff(self):
        return TestRiff()

class ModelListViewTestCase(BaseModelViewTestCase):
    def setUp(self):
        super(ModelListViewTestCase, self).setUp()
        self.view = ModelListView.as_view(riff=self.riff,
                                          model=ContentType,
                                          form_class=self.form_class,)

    def test_get_list(self):
        request = self.request_factory.get('/')
        response = self.view(request)
    
    def test_post_create(self):
        request = self.request_factory.post('/')
        response = self.view(request)

class ModelDetailViewTestCase(BaseModelViewTestCase):
    def setUp(self):
        super(ModelDetailViewTestCase, self).setUp()
        
        self.view = ModelDetailView.as_view(riff=self.riff,
                                            model=ContentType,
                                            form_class=self.form_class,)

    def get_an_object(self):
        return ContentType.objects.all()[0]

    def test_get_detail(self):
        request = self.request_factory.get('/')
        response = self.view(request, pk=self.get_an_object().pk)

    def test_post_detail(self):
        request = self.request_factory.post('/')
        response = self.view(request, pk=self.get_an_object().pk)

class ModelDeleteViewTestCase(BaseModelViewTestCase):
    def setUp(self):
        super(ModelDeleteViewTestCase, self).setUp()
        
        self.view = ModelDeleteView.as_view(riff=self.riff,
                                            model=ContentType,)

    def get_an_object(self):
        return ContentType.objects.all()[0]

    def test_get_delete(self):
        request = self.request_factory.get('/')
        response = self.view(request, pk=self.get_an_object().pk)

    def test_post_delete(self):
        request = self.request_factory.post('/')
        response = self.view(request, pk=self.get_an_object().pk)

