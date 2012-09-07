from django.conf.urls import patterns, url

from djam.riffs.base import Riff
from djam.views.dashboard import DashboardView


class DashboardRiff(Riff):
    dashboard_view = DashboardView
    verbose_name = 'Dashboard'

    def get_extra_urls(self):
        return patterns('',
            url(r'^$',
                self.wrap_view(self.dashboard_view.as_view(**self.get_view_kwargs())),
                name='dashboard')
        )

    def get_default_url(self):
        return self.reverse('dashboard')
