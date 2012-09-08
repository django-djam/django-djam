from django.conf.urls import patterns, include, url
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

from djam.riffs.base import Riff
from djam.riffs.auth import AuthRiff
from djam.riffs.dashboard import DashboardRiff


class AdminRiff(Riff):
    auth_riff_class = AuthRiff
    riff_classes = (DashboardRiff,)
    slug = 'admin'

    def __init__(self, namespace=None, app_name=None):
        site_name = Site.objects.get_current().name
        if self.verbose_name is None:
            self.verbose_name = _('Admin for {site_name}'.format(site_name=site_name))
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


admin = AdminRiff(app_name='djam')
