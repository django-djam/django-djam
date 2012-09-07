from django.conf.urls import patterns, include, url
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

from djam.riffs.base import Riff
from djam.riffs.auth import AuthRiff


class AdminRiff(Riff):
    riff_classes = (AuthRiff,)
    slug = 'admin'

    def __init__(self, namespace=None, app_name=None):
        site_name = Site.objects.get_current().name
        self.verbose_name = _('Admin for {site_name}'.format(site_name=site_name))
        super(AdminRiff, self).__init__(parent=None,
                                        namespace=None,
                                        app_name=None)


admin = AdminRiff(app_name='djam')
