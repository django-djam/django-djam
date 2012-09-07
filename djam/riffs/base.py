from django.conf.urls.defaults import patterns, include, url
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.template.defaultfilters import slugify

from urllib import urlencode


class Riff(object):
    widgets = []
    riff_classes = []
    verbose_name = None
    slug = None
    namespace = None
    app_name = 'djam'

    def __init__(self, namespace=None, parent=None):
        self.parent = parent
        if self.verbose_name is None:
            raise ImproperlyConfigured('Please give me a verbose name')
        if self.slug is None:
            self.slug = slugify(self.verbose_name)
        self.namespace = namespace or self.namespace or self.slug
        self._riffs = []
        for riff_class in self.riff_classes:
            riff = riff_class(parent=self)
            self._riffs.append(riff)

    def get_urls(self):
        urlpatterns = self.get_extra_urls()

        for riff in self._riffs:
            urlpatterns += patterns('',
                url(r'^{slug}/'.format(slug=riff.slug),
                    include(riff.get_urls_tuple())),
            )

        return urlpatterns

    def get_extra_urls(self):
        return patterns('',)

    def get_urls_tuple(self):
        return self.get_urls(), self.app_name, self.namespace

    def get_view_kwargs(self):
        return {'riff':self,}

    def has_permission(self, request):
        if self.parent:
            return self.parent.has_permission(request)
        return True

    def get_unauthorized_response(self, request):
        params = {'next':request.path}
        params = urlencode(params)
        return HttpResponseRedirect('{url}?{params}'.format(url=self.reverse('login'), params=params))

    def wrap_view(self, view):
        return view

    def reverse(self, name, *args, **kwargs):
        return reverse('{namespace}:{viewname}'.format(namespace=self.namespace, viewname=name), args=args, kwargs=kwargs)
