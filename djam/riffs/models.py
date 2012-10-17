from __future__ import unicode_literals

from django.conf.urls.defaults import patterns, url
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ImproperlyConfigured
from django.forms.models import modelform_factory
import floppyforms as forms

from djam.riffs.base import Riff
from djam.views.models import ModelListView, ModelCreateView, ModelUpdateView, ModelDeleteView


class ModelRiff(Riff):
    model = None
    list_view = ModelListView
    create_view = ModelCreateView
    update_view = ModelUpdateView
    delete_view = ModelDeleteView

    create_form_class = None
    create_form_fields = None
    create_form_exclude = None

    update_form_class = None
    update_form_fields = None
    update_form_exclude = None

    def __init__(self, *args, **kwargs):
        if not self.model:
            raise ImproperlyConfigured('Please specify a model')
        if self.verbose_name is None:
            self.verbose_name = self.model._meta.verbose_name
        if self.verbose_name_plural is None:
            self.verbose_name_plural = self.model._meta.verbose_name_plural
        if self.slug is None:
            self.slug = self.model._meta.module_name
        if self.namespace is None:
            self.namespace = '{appname}_{modelname}'.format(
                appname=self.model._meta.app_label,
                modelname=self.model._meta.module_name)
        super(ModelRiff, self).__init__(*args, **kwargs)

    def get_extra_urls(self):
        init = self.get_view_kwargs()

        return patterns('',
            url(r'^$',
                self.wrap_view(self.list_view.as_view(**init)),
                name='list'),
            url(r'^add/$',
                self.wrap_view(self.create_view.as_view(**self.get_create_view_kwargs())),
                name='create'),
            url(r'^(?P<pk>\w+)/$',
                self.wrap_view(self.update_view.as_view(**self.get_update_view_kwargs())),
                name='update'),
            url(r'^(?P<pk>\w+)/delete/$',
                self.wrap_view(self.delete_view.as_view(**init)),
                name='delete'),
        )

    def get_default_url(self):
        return self.reverse('list'.format(appname=self.model._meta.app_label, modelname=self.slug))

    def get_view_kwargs(self):
        kwargs = super(ModelRiff, self).get_view_kwargs()
        kwargs['model'] = self.model
        return kwargs

    def get_update_view_kwargs(self):
        kwargs = self.get_view_kwargs()
        base_form_class = self.update_form_class or forms.ModelForm
        form_class = modelform_factory(self.model, base_form_class,
                                       fields=self.update_form_fields,
                                       exclude=self.update_form_exclude)
        kwargs['form_class'] = form_class
        return kwargs
    
    def get_create_view_kwargs(self):
        kwargs = self.get_view_kwargs()
        base_form_class = self.create_form_class or forms.ModelForm
        form_class = modelform_factory(self.model, base_form_class,
                                       fields=self.create_form_fields,
                                       exclude=self.create_form_exclude)
        kwargs['form_class'] = form_class
        return kwargs


class UserRiff(ModelRiff):
    model = User
    create_form_class = UserCreationForm
    update_form_class = UserChangeForm
