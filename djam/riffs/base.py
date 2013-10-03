from __future__ import unicode_literals

from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseForbidden
from django.template.defaultfilters import slugify
from django.utils.datastructures import SortedDict

from djam.views.base import DefaultRedirectView


class Riff(object):
    widgets = []
    riff_classes = []
    display_name = None
    slug = None
    namespace = None
    app_name = None
    default_redirect_view = DefaultRedirectView
    widget_template = 'djam/_widget.html'

    def __init__(self, parent=None, namespace=None, app_name=None):
        self.parent = parent
        if self.display_name is None:
            raise ImproperlyConfigured('Please give me a display name')
        if self.slug is None:
            self.slug = slugify(self.display_name)
        self.namespace = namespace or self.namespace or self.slug
        if parent is None:
            self.base_riff = self
            self.path = (self,)
        else:
            self.base_riff = parent.base_riff
            self.path = parent.path + (self,)
        self._riffs = SortedDict()
        for riff_class in self.riff_classes:
            self.register(riff_class)

    def __getitem__(self, key):
        return self._riffs[key]

    def sort_riffs(self, key=None, reverse=False):
        if key is None:
            key = lambda r: r.display_name
        riffs = sorted(self._riffs.itervalues(), key=key, reverse=reverse)
        self._riffs.keyOrder = [r.namespace for r in riffs]

    @property
    def riffs(self):
        return self._riffs.values()

    def get_default_url(self):
        """
        Returns the default base url for this riff. Must be implemented by
        subclasses.

        """
        raise NotImplementedError('Subclasses must implement get_default_url.')

    def get_urls(self):
        urlpatterns = self.get_extra_urls()

        for riff in self.riffs:
            pattern = r'^{0}/'.format(riff.slug) if riff.slug else r'^'
            urlpatterns += patterns('',
                url(pattern, include(riff.urls)),
            )

        if self.default_redirect_view is not None:
            urlpatterns += patterns('',
                url(r'^$', self.default_redirect_view.as_view(riff=self)),
            )

        return urlpatterns

    def get_extra_urls(self):
        return patterns('',)

    @property
    def urls(self):
        return self.get_urls(), self.app_name, self.namespace

    def get_view_kwargs(self):
        return {'riff': self}

    def has_permission(self, request):
        if self.parent:
            return self.parent.has_permission(request)
        return True

    def is_hidden(self, request):
        return not self.has_permission(request)

    def get_unauthorized_response(self, request):
        if self.base_riff is not self:
            return self.base_riff.get_unauthorized_response(request)
        return HttpResponseForbidden()

    def wrap_view(self, view):
        return view

    def reverse(self, name, args=None, kwargs=None):
        return reverse('{namespace}:{viewname}'.format(namespace=self.full_namespace, viewname=name),
                       args=args, kwargs=kwargs)

    @property
    def full_namespace(self):
        return ":".join([r.namespace for r in self.path])

    def register(self, riff_class):
        riff = riff_class(parent=self)
        if riff.namespace in self._riffs:
            raise ValueError("Riff with namespace {0} already "
                             "registered.".format(riff.namespace))
        self._riffs[riff.namespace] = riff
