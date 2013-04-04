from __future__ import unicode_literals
from urllib import urlencode

from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from djam.riffs.base import Riff
from djam.riffs.auth import AuthRiff
from djam.riffs.dashboard import DashboardRiff
from djam.riffs.models import ModelRiff


class AdminRiff(Riff):
    riff_classes = [AuthRiff, DashboardRiff]
    display_name = _('Djam Admin')
    slug = 'admin'
    namespace = 'djam'
    # Disable default redirect view.
    default_redirect_view = None

    def get_default_url(self):
        return self['dashboard'].get_default_url()

    def has_permission(self, request):
        return request.user.is_active and request.user.is_authenticated()

    def get_unauthorized_response(self, request):
        params = {'next': request.path}
        params = urlencode(params)
        return HttpResponseRedirect('{url}?{params}'.format(url=self['auth'].reverse('login'), params=params))

    def register_model(self, model):
        # Think up a reasonable name.
        class_name = model.__name__ + str('Riff')
        riff_class = type(class_name, (ModelRiff,), {'model': model})
        self.register(riff_class)


admin = AdminRiff(app_name='djam')
