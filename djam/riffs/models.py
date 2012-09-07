# Trick django into treating us as an app.
from django.conf.urls.defaults import patterns
from django.core.exceptions import ImproperlyConfigured
from django import forms

from djam.riffs.base import Riff

class ModelRiff(Riff):
    model = None
    list_view = None
    detail_view = None
    delete_view = None
    history_view = None
    
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
        urlpatterns = super(SiteRiff, self).get_urls()
        
        def wrap(view):
            return self.as_view(view)
        
        init = self.get_view_kwargs()
        
        format_params = {
            'appname': self.model._meta.app_label,
            'modelname': self.slug
        }
        
        urlpatterns += patterns('',
            url(r'^/$',
                wrap(self.list_view.as_view(**init)),
                name='{appname}_{modelname}_list'.format(**format_params),
            url(r'^(?P<pk>\w+)/$',
                wrap(self.detail_view.as_view(**init)),
                name='{appname}_{modelname}_change').format(**format_params),
            url(r'^(?P<pk>\w+)/delete/$',
                wrap(self.delete_view.as_view(**init)),
                name='{appname}_{modelname}_delete').format(**format_params),
            url(r'^(?P<pk>\w+)/history/$',
                wrap(self.history_view.as_view(**init)),
                name='{appname}_{modelname}_history').format(**format_params),
        )
        
        return urlpatterns
    
    def get_form_class(self):
        if self.form_class:
            return self.form_class
        class GeneratedForm(forms.ModelForm):
            class Meta:
                model = self.model
        return GeneratedForm


