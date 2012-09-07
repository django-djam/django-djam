from django.conf.urls.defaults import patterns, include
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.template.defaultfilters import slugify

from urllib import urlencode

class Riff(object):
    widgets = []
    riffs = []
    verbose_name = None
    slug = None
    
    def __init__(self, name='djadmin', parent_riff=None):
        self.name = name
        self.parent_riff = parent_riff
        if self.verbose_name is None:
            raise ImproperlyConfigured('Please give me a verbose name')
        if self.slug is None:
            self.slug = slugify(self.verbose_name)
        self._riffs = list() #TODO better name
        for riff_cls in self.riffs:
            riff = riff_cls(parent_riff=self)
            self._riffs.append(riff)
    
    def get_urls(self):
        urlpatterns = self.get_extra_urls()
        
        for riff in self._riffs:
            urlpatterns += patterns('',
                url(r'^{slug}/'.format(slug=riff.slug),
                    include(riff.get_urls())),
            )
        return urlpatterns
    
    def get_extra_urls(self):
        return patterns('',)
    
    def urls(self):
        return self.get_urls(), None, self.name
    urls = property(urls)
    
    def get_view_kwargs(self):
        return {'riff':self,}
    
    def has_permission(self, request):
        if self.parent_riff:
            return self.parent_riff.has_permission(request)
        return True
    
    def get_unauthorized_response(self, request):
        params = {'next':request.path}
        params = urlencode(params)
        return HttpResponseRedirect('{url}?{params}'.format(url=self.reverse('login'), params=params))
    
    def as_view(self, view):
        return view
    
    def reverse(self, name, *args, **kwargs):
        return reverse('{namespace}:{viewname}'.format(namespace=self.namespace, viewname=name), args=args, kwargs=kwargs)

