from __future__ import unicode_literals
from urllib import urlencode

from django.conf.urls import patterns, include, url
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from djam.riffs.base import Riff
from djam.riffs.auth import AuthRiff
from djam.riffs.dashboard import DashboardRiff
from djam.riffs.models import ModelRiff


class AdminRiff(Riff):
    auth_riff_class = AuthRiff
    riff_classes = (DashboardRiff,)
    display_name = _('Djam Admin')
    slug = 'admin'

    def __init__(self, namespace=None, app_name=None):
        super(AdminRiff, self).__init__(parent=None,
                                        namespace=None,
                                        app_name=None)
        self.auth_riff = self.auth_riff_class(parent=self)

    def get_default_url(self):
        return self.riffs[0].get_default_url()

    def get_extra_urls(self):
        return patterns('',
            url(r'^', include(self.auth_riff.get_urls_tuple()))
        )

    def has_permission(self, request):
        return request.user.is_active and request.user.is_authenticated()

    def get_unauthorized_response(self, request):
        params = {'next':request.path}
        params = urlencode(params)
        return HttpResponseRedirect('{url}?{params}'.format(url=self.auth_riff.reverse('login'), params=params))


class ModelAdminRiff(AdminRiff):
    def register_model(self, model, riff_class=None):
        if riff_class is None:
            # Think up a reasonable name.
            class_name = model.__name__ + str('Riff')
            riff_class = type(class_name, (ModelRiff,), {'model': model})

        self.riffs.append(riff_class(parent=self))


admin = ModelAdminRiff(app_name='djam')
