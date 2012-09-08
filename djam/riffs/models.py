# Trick django into treating us as an app.
from django.conf.urls.defaults import patterns, url
from django.core.exceptions import ImproperlyConfigured
from django import forms

from djam.riffs.base import Riff
from djam.views.models import ModelListView, ModelCreateView, ModelDetailView, ModelDeleteView, ModelHistoryView


class ModelRiff(Riff):
    model = None
    list_view = ModelListView
    create_view = ModelCreateView
    detail_view = ModelDetailView
    delete_view = ModelDeleteView
    history_view = ModelHistoryView

    base_form_class = forms.ModelForm
    form_class = None

    def __init__(self, *args, **kwargs):
        if not self.model:
            raise ImproperlyConfigured('Please specify a model')
        if self.verbose_name is None:
            self.verbose_name = self.model._meta.verbose_name
        if self.slug is None:
            self.slug = self.model._meta.module_name
        super(ModelRiff, self).__init__(*args, **kwargs)

    def get_urls(self):
        urlpatterns = super(ModelRiff, self).get_urls()

        init = self.get_view_kwargs()

        format_params = {
            'appname': self.model._meta.app_label,
            'modelname': self.slug
        }

        urlpatterns += patterns('',
            url(r'^/$',
                self.wrap_view(self.list_view.as_view(**init)),
                name='{appname}_{modelname}_list'.format(**format_params)),
            url(r'^add/$',
                self.wrap_view(self.create_view.as_view(**self.get_create_view_kwargs())),
                name='{appname}_{modelname}_add'.format(**format_params)),
            url(r'^(?P<pk>\w+)/$',
                self.wrap_view(self.detail_view.as_view(**self.get_detail_view_kwargs())),
                name='{appname}_{modelname}_change'.format(**format_params)),
            url(r'^(?P<pk>\w+)/delete/$',
                self.wrap_view(self.delete_view.as_view(**init)),
                name='{appname}_{modelname}_delete'.format(**format_params)),
            url(r'^(?P<pk>\w+)/history/$',
                self.wrap_view(self.history_view.as_view(**init)),
                name='{appname}_{modelname}_history'.format(**format_params)),
        )

        return urlpatterns

    def get_default_url(self):
        return self.reverse('{appname}_{modelname}_list'.format(appname=self.model._meta.app_label, modelname=self.slug))

    def get_form_class(self):
        if self.form_class:
            return self.form_class
        class GeneratedForm(forms.ModelForm):
            class Meta:
                model = self.model
        return GeneratedForm

    def get_view_kwargs(self):
        kwargs = super(ModelRiff, self).get_view_kwargs()
        kwargs['model'] = self.model
        return kwargs

    def get_detail_view_kwargs(self):
        kwargs = self.get_view_kwargs()
        kwargs['form_class'] = self.get_form_class()
        return kwargs
    
    def get_create_view_kwargs(self):
        kwargs = self.get_view_kwargs()
        kwargs['form_class'] = self.get_form_class()
        return kwargs

