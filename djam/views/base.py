from __future__ import unicode_literals

from django.utils.cache import add_never_cache_headers
from django.views.generic import RedirectView


class RiffViewMixin(object):
    riff = None
    cacheable = False
    
    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission(request):
            return self.get_unauthorized_response(request)

        response = super(RiffViewMixin, self).dispatch(request, *args, **kwargs)
        if not self.cacheable:
            add_never_cache_headers(response)
        return response
    
    def has_permission(self, request):
        return self.riff.has_permission(request)
    
    def get_unauthorized_response(self, request):
        return self.riff.get_unauthorized_response(request)

    def get_crumbs(self):
        """
        Returns a list of breadcrumbs - (url, name) tuples.

        """
        return [(r.get_default_url, r.display_name) for r in self.riff.path]

    def get_context_data(self, **kwargs):
        context = super(RiffViewMixin, self).get_context_data(**kwargs)
        context.update({
            'base_riff': self.riff.base_riff,
            'riff': self.riff,
            'crumbs': self.get_crumbs(),
        })
        return context


class DefaultRedirectView(RiffViewMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, **kwargs):
        return self.riff.get_default_url()
