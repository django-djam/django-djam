from __future__ import unicode_literals
import json
from urllib import urlencode
import warnings

from django.conf import settings
from django.conf.urls import patterns, url
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.utils.encoding import force_text
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule
from django.utils.translation import ugettext_lazy as _

from djam.riffs.base import Riff
from djam.riffs.models import ModelRiff


class AdminRiff(Riff):
    display_name = _('Admin')
    slug = 'admin'
    namespace = 'djam'
    # Disable default redirect view.
    default_redirect_view = None
    _autodiscovered = False

    def get_default_url(self):
        return self['dashboard'].get_default_url()

    def get_extra_urls(self):
        urlpatterns = patterns('',
            url(r'^genrelinfo/(?P<pk>\d+)/$',
                self._genrelinfo,
                name="genrelinfo")
        )
        return urlpatterns

    def _genrelinfo(self, request, pk):
        if not request.is_ajax():
            raise Http404("Not AJAX.")
        try:
            ct = ContentType.objects.get_for_id(pk)
        except ContentType.DoesNotExist:
            data = {
                'choices': []
            }
            if settings.DEBUG:
                data['error'] = "Content type not found."
        else:
            model = ct.model_class()

            for riff in self.riffs:
                if getattr(riff, 'model', None) == model:
                    break
            else:
                riff = None

            if riff is None or not riff.has_permission(request):
                data = {
                    'choices': []
                }
                if settings.DEBUG:
                    if riff is None:
                        data['error'] = "No riff found."
                    else:
                        data['error'] = "Not enough permissions."
            else:
                data = {
                    'add_url': riff.reverse('create'),
                    'choices': [(instance.pk, force_text(instance))
                                for instance in model.objects.all()]
                }
        return HttpResponse(json.dumps(data), content_type="application/json")

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
            if with_modeladmins:
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

            if with_modeladmins:
                for model in site._registry:
                    try:
                        self.register_model(model)
                    except ValueError:
                        pass
            self.sort_riffs()
            self._autodiscovered = True


admin = AdminRiff(app_name='djam')
