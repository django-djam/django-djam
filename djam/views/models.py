from __future__ import unicode_literals

from django.contrib.admin.util import flatten_fieldsets
from django.forms.models import modelform_factory
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _
import floppyforms

from djam.forms import QueryForm
from djam.views.base import RiffViewMixin


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
        fieldsets = self.fieldsets or ((None, {'fields': list(context['form'].fields)}),)
        context.update({
            'fieldsets': fieldsets,
            'readonly': self.readonly,
        })
        return context


class ModelRiffMixin(RiffViewMixin):
    template_name_suffix = None

    def get_template_names(self):
        if self.template_name:
            return [self.template_name]

        applabel = self.model._meta.app_label
        slug = self.riff.slug

        return ['djam/models/{applabel}/{modelname}/{suffix}.html'.format(suffix=self.template_name_suffix, applabel=applabel, modelname=slug),
                'djam/models/{applabel}/{suffix}.html'.format(suffix=self.template_name_suffix, applabel=applabel),
                'djam/models/{suffix}.html'.format(suffix=self.template_name_suffix)]

    def get_context_data(self, **kwargs):
        context = super(ModelRiffMixin, self).get_context_data(**kwargs)
        context.update({
            'verbose_name': self.model._meta.verbose_name,
            'verbose_name_plural': self.model._meta.verbose_name_plural,
        })
        return context


def unicode_column(obj):
    return force_unicode(obj)
unicode_column.short_description = 'unicode'
unicode_column.do_not_call_in_templates = True


class ModelListView(ModelRiffMixin, ListView):
    template_name_suffix = 'list'
    columns = (unicode_column,)
    link_columns = None
    per_page = 100
    filters = None
    search = None
    #: May be a list of fields to use to order the list. Currently
    #: only the first field will actually be used.
    order = None

    def get_queryset(self):
        queryset = super(ModelListView, self).get_queryset()
        data = self.request.GET.copy()
        if 'order' not in data:
            order = self.order or self.model._meta.ordering
            if order:
                data['order'] = order[0]
        self.form = QueryForm(queryset, self.filters, self.columns,
                              self.search, data=data)
        return self.form.get_queryset()

    def get_context_data(self, **kwargs):
        context = super(ModelListView, self).get_context_data(**kwargs)
        context.update({
            'columns': self.columns,
            'link_columns': self.link_columns or self.columns[:1],
            'query_form': self.form,
        })
        return context


class ModelCreateView(FloppyformsMixin, ModelRiffMixin, CreateView):
    template_name_suffix = 'create'

    def get_success_url(self):
        return self.riff.reverse('update', pk=self.object.pk)

    def get_context_data(self, **kwargs):
        context = super(ModelCreateView, self).get_context_data(**kwargs)
        context.update(page_title=_('Add a {0}'.format(self.model._meta.verbose_name)))
        return context


class ModelUpdateView(FloppyformsMixin, ModelRiffMixin, UpdateView):
    template_name_suffix = 'update'

    def get_success_url(self):
        return self.riff.reverse('update', pk=self.object.pk)

    def get_context_data(self, **kwargs):
        context = super(ModelUpdateView, self).get_context_data(**kwargs)
        context.update(page_title=unicode(self.object))
        return context


class ModelDeleteView(ModelRiffMixin, DeleteView):
    template_name_suffix = 'delete'

    def get_success_url(self):
        return self.riff.get_default_url()

    def get_context_data(self, **kwargs):
        context = super(ModelDeleteView, self).get_context_data(**kwargs)
        context.update(page_title=_('Delete {0}'.format(unicode(self.object))))
        return context
