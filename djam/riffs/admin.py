from __future__ import unicode_literals
from urllib import urlencode
import warnings

from django.http import HttpResponseRedirect
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule
from django.utils.translation import ugettext_lazy as _

from djam.riffs.base import Riff


class AdminRiff(Riff):
    display_name = _('Djam Admin')
    slug = 'admin'
    namespace = 'djam'
    # Disable default redirect view.
    default_redirect_view = None
    _autodiscovered = False

    def get_default_url(self):
        return self['dashboard'].get_default_url()

    def has_permission(self, request):
        return request.user.is_active and request.user.is_authenticated()

    def get_unauthorized_response(self, request):
        params = {'next': request.path}
        params = urlencode(params)
        return HttpResponseRedirect('{url}?{params}'.format(url=self['auth'].reverse('login'), params=params))

    def register_model(self, model):
        from djam.riffs.models import ModelRiff
        # Think up a reasonable name.
        class_name = model.__name__ + str('Riff')
        riff_class = type(class_name, (ModelRiff,), {'model': model})
        self.register(riff_class)

    def register_module(self, module_name):
        mod = import_module(module_name)

        if not hasattr(mod, 'riffs'):
            warnings.warn('Module {0} has no attribute "riffs".'
                          ''.format(module_name))
            return

        # Let the attribute error be raised if there's an issue.
        for riff in mod.riffs:
            try:
                self.register(riff)
            except ValueError:
                pass

    def autodiscover(self, with_batteries=True, with_modeladmins=True):
        """
        :func:`djam.autodiscover` loops through ``INSTALLED_APPS`` and loads
        any ``riffs.py`` modules in those apps - similar to the django admin's
        autodiscovery.

        On top of that, :mod:`djam` will by default include
        :class:`ModelRiffs <ModelRiff>` which have been auto-generated from
        registered ModelAdmins. This can be turned of by passing in
        ``with_modeladmins=False``.

        For some commonly-used models (such as ``django.contrib.auth.User``)
        :mod:`djam` provides a Riff which handles some functionality that
        would otherwise be lost during the conversion from ModelAdmin to
        :class:`ModelRiff`. This can be disabled by passing in
        ``with_batteries=False``.

        The order that these are loaded is: app riff modules, "batteries",
        and ModelAdmins. If two riffs are registered using the same namespace,
        the  first one registered will take precedence; any others will be
        ignored.

        """
        if not self._autodiscovered:
            from django.conf import settings
            from django.contrib.admin import autodiscover, site
            autodiscover()

            # for app in installed_apps register module
            for app in settings.INSTALLED_APPS:
                # Don't register riffs from djam.riffs.
                if app == 'djam':
                    continue

                mod = import_module(app)
                before_import = self._riffs.copy()

                try:
                    self.register_module('{0}.riffs'.format(app))
                except:
                    # Reset riffs registry.
                    self._riffs = before_import

                    # If the app has a riffs module, but something went wrong,
                    # reraise the exception.
                    if module_has_submodule(mod, 'riffs'):
                        raise

            if with_batteries:
                self.register_module('djam.batteries')

            for model in site._registry:
                try:
                    self.register_model(model)
                except ValueError:
                    pass
            self.sort_riffs()
            self._autodiscovered = True


admin = AdminRiff(app_name='djam')
