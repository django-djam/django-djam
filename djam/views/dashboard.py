from django.views.generic import TemplateView

from djam.views.base import RiffViewMixin


class DashboardView(RiffViewMixin, TemplateView):
    template_name = 'djam/dashboard/dashboard.html'
