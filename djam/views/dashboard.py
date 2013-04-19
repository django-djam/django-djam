from __future__ import unicode_literals

from djam.views.generic import TemplateView


class DashboardView(TemplateView):
    template_name = 'djam/dashboard/dashboard.html'
