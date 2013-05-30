from __future__ import unicode_literals

from django.contrib.admin.util import flatten_fieldsets
from django.db import models
from django.forms.models import (modelform_factory, ModelChoiceField,
                                 ModelMultipleChoiceField)
from django.utils.cache import add_never_cache_headers
from django.utils.translation import ugettext as _, string_concat
from django.views import generic
import floppyforms

from djam.widgets import AddWrapper


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

    def get_context_data(self, **kwargs):
        context = super(FloppyformsMixin, self).get_context_data(**kwargs)
        fieldsets = (self.fieldsets or
                     ((None, {'fields': list(context['form'].fields)}),))
        context.update({
            'fieldsets': fieldsets,
            'readonly': self.readonly,
        })
        return context


class ModelFloppyformsMixin(FloppyformsMixin):
    def get_form_field(self, db_field, **kwargs):
        field = db_field.formfield(**kwargs)
        if field:
            field.widget.attrs['data-required'] = int(field.required)
        if issubclass(db_field.__class__, models.ManyToManyField):
            msg = _('Hold down "Control", or "Command" on a Mac, to select more than one.')
            msg = unicode(string_concat(' ', msg))
            if field.help_text.endswith(msg):
                field.help_text = field.help_text[:-len(msg)]
        if isinstance(field, ModelChoiceField):
            model = field.queryset.model
            if isinstance(field, ModelMultipleChoiceField):
                msg = string_concat(_("Choose some "),
                                    model._meta.verbose_name_plural,
                                    "...")
            else:
                msg = string_concat(_("Choose a "),
                                    model._meta.verbose_name,
                                    "...")
            field.widget.attrs['data-placeholder'] = msg

            for riff in self.riff.base_riff.riffs:
                if getattr(riff, 'model', None) == model:
                    if riff.has_add_permission(self.request):
                        field.widget = AddWrapper(field.widget, riff)
                    break
        return field

    def get_form_class(self):
        if self.form_class:
            form_class = self.form_class
        else:
            form_class = floppyforms.ModelForm
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
                                 form=form_class,
                                 exclude=self.readonly,
                                 fields=fields,
                                 formfield_callback=self.get_form_field)


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


class CreateView(ModelFloppyformsMixin, RiffViewMixin, generic.CreateView):
    pass


class UpdateView(ModelFloppyformsMixin, RiffViewMixin, generic.UpdateView):
    pass


class DeleteView(RiffViewMixin, generic.DeleteView):
    pass


class ListView(RiffViewMixin, generic.ListView):
    pass
