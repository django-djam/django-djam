from __future__ import unicode_literals
from urllib import urlencode

from django.conf.urls import patterns, include, url
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from djam.riffs.base import Riff
from djam.riffs.auth import AuthRiff
from djam.riffs.dashboard import DashboardRiff
from djam.riffs.models import ModelRiff


class AdminRiff(Riff):
    auth_riff_class = AuthRiff
    dashboard_riff_class = DashboardRiff
    display_name = _('Djam Admin')
    slug = 'admin'
    namespace = 'djam'

    def __init__(self, namespace=None, app_name=None):
        super(AdminRiff, self).__init__(parent=None,
                                        namespace=None,
                                        app_name=None)
        self.auth_riff = self.auth_riff_class(parent=self)
        self.dashboard_riff = self.dashboard_riff_class(parent=self)

    def get_default_url(self):
        return self.dashboard_riff.get_default_url()

    def get_extra_urls(self):
        return patterns('',
            url(r'^', include(self.dashboard_riff.get_urls_tuple())),
            url(r'^', include(self.auth_riff.get_urls_tuple())),
        )

    def has_permission(self, request):
        return request.user.is_active and request.user.is_authenticated()

    def get_unauthorized_response(self, request):
        params = {'next':request.path}
        params = urlencode(params)
        return HttpResponseRedirect('{url}?{params}'.format(url=self.auth_riff.reverse('login'), params=params))

    def register(self, riff_class):
        self.riffs.append(riff_class(parent=self))

    def register_model(self, model):
        # Think up a reasonable name.
        class_name = model.__name__ + str('Riff')
        riff_class = type(class_name, (ModelRiff,), {'model': model})
        self.register(riff_class)


admin = AdminRiff(app_name='djam')
