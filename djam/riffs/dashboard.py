from __future__ import unicode_literals

from django.conf.urls import patterns, url
from django.utils.translation import ugettext_lazy as _

from djam.riffs.base import Riff
from djam.views.dashboard import DashboardView


class DashboardRiff(Riff):
    dashboard_view = DashboardView
    display_name = _('Dashboard')

    def get_extra_urls(self):
        return patterns('',
            url(r'^$',
                self.wrap_view(self.dashboard_view.as_view(**self.get_view_kwargs())),
                name='dashboard')
        )

    def get_default_url(self):
        return self.reverse('dashboard')

    def is_hidden(self, request):
        """Always returns True to hide the dashboard."""
        return True
