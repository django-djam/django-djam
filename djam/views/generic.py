from __future__ import unicode_literals

from django.contrib.admin.util import flatten_fieldsets
from django.forms.models import modelform_factory
from django.utils.cache import add_never_cache_headers
from django.views import generic
import floppyforms


class RiffViewMixin(object):
    riff = None
    cacheable = False

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission(request):
            return self.get_unauthorized_response(request)

        response = super(RiffViewMixin, self).dispatch(request, *args, **kwargs)
        if not self.cacheable:
            add_never_cache_headers(response)
        return response

    def has_permission(self, request):
        return self.riff.has_permission(request)

    def get_unauthorized_response(self, request):
        return self.riff.get_unauthorized_response(request)

    def get_crumbs(self):
        """
        Returns a list of breadcrumbs - (url, name) tuples.

        """
        return [(r.get_default_url, r.display_name) for r in self.riff.path]

    def get_context_data(self, **kwargs):
        context = super(RiffViewMixin, self).get_context_data(**kwargs)
        context.update({
            'base_riff': self.riff.base_riff,
            'riff': self.riff,
            'crumbs': self.get_crumbs(),
        })
        return context


class FloppyformsMixin(object):
    fieldsets = None
    readonly = ()

    def get_form_class(self):
        # This is mostly a copy of django's FormMixin.get_form_class,
        # but it a) uses floppyforms by default, and b) supports fields
        # and exclusions.
        if self.form_class:
            return self.form_class
        else:
            if self.model is not None:
                model = self.model
            elif hasattr(self, 'object') and self.object is not None:
                model = self.object.__class__
            else:
                model = self.get_queryset().model
            if self.fieldsets:
                fields = flatten_fieldsets(self.fieldsets)
            else:
                fields = None
            return modelform_factory(model,
                                     form=floppyforms.ModelForm,
                                     exclude=self.readonly,
                                     fields=fields)

    def get_context_data(self, **kwargs):
        context = super(FloppyformsMixin, self).get_context_data(**kwargs)
        fieldsets = (self.fieldsets or
                     ((None, {'fields': list(context['form'].fields)}),))
        context.update({
            'fieldsets': fieldsets,
            'readonly': self.readonly,
        })
        return context


class View(RiffViewMixin, generic.View):
    pass


class TemplateView(RiffViewMixin, generic.TemplateView):
    pass


class RedirectView(RiffViewMixin, generic.RedirectView):
    pass


class ArchiveIndexView(RiffViewMixin, generic.ArchiveIndexView):
    pass


class YearArchiveView(RiffViewMixin, generic.YearArchiveView):
    pass


class MonthArchiveView(RiffViewMixin, generic.MonthArchiveView):
    pass


class WeekArchiveView(RiffViewMixin, generic.WeekArchiveView):
    pass


class DayArchiveView(RiffViewMixin, generic.DayArchiveView):
    pass


class TodayArchiveView(RiffViewMixin, generic.TodayArchiveView):
    pass


class DateDetailView(RiffViewMixin, generic.DateDetailView):
    pass


class DetailView(RiffViewMixin, generic.DetailView):
    pass


class FormView(FloppyformsMixin, RiffViewMixin, generic.FormView):
    pass


class CreateView(FloppyformsMixin, RiffViewMixin, generic.CreateView):
    pass


class UpdateView(FloppyformsMixin, RiffViewMixin, generic.UpdateView):
    pass


class DeleteView(RiffViewMixin, generic.DeleteView):
    pass


class ListView(RiffViewMixin, generic.ListView):
    pass
