from __future__ import unicode_literals

import operator

from django.db import models
from django.contrib.admin.util import flatten_fieldsets, lookup_needs_distinct
from django.forms.models import modelform_factory
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.utils.translation import ugettext_lazy as _
import floppyforms

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


class ModelListView(ModelRiffMixin, ListView):
    template_name_suffix = 'list'
    unicode_func = lambda obj: unicode(obj)
    unicode_func.short_description = 'unicode'
    unicode_func.do_not_call_in_templates = True
    columns = (unicode_func,)
    link_columns = None
    per_page = 100
    filters = None
    search = None

    def _search_lookup(self, field):
        # returns a lookup for searching a database field based
        # on a shortcut name.
        if field[0] in ('^', '=', '@'):
            if field.startswith('^'):
                lookup = 'istartswith'
            elif field.startswith('='):
                lookup = 'iexact'
            elif field.startswith('@'):
                lookup = 'icontains'
            field = field[1:]
        else:
            lookup = 'icontains'
        return "{0}__{1}".format(field, lookup)

    def _search(self, queryset):
        query = self.request.GET.get('search')
        use_distinct = False
        if self.search and query:
            lookups = [self._search_lookup(str(field))
                       for field in self.search]
            for bit in query.split():
                or_qlist = [models.Q(**{lookup: bit}) for lookup in lookups]
                queryset = queryset.filter(reduce(operator.or_, or_qlist))

            if not use_distinct:
                for lookup in lookups:
                    if lookup_needs_distinct(self.model._meta, lookup):
                        use_distinct = True
                        break

        if use_distinct:
            queryset = queryset.distinct()

        return queryset

    def _select_related(self, queryset):
        # If the queryset doesn't already have select_related defined,
        # check the columns option to auto-select ManyToOne rels that
        # will be used.
        if not queryset.query.select_related:
            related = []
            for field_name in self.columns:
                try:
                    field = self.model._meta.get_field(field_name)
                except models.FieldDoesNotExist:
                    pass
                else:
                    if isinstance(field.rel, models.ManyToOneRel):
                        related.append(field_name)
            if related:
                queryset = queryset.select_related(*related)
        return queryset

    def get_queryset(self):
        queryset = super(ModelListView, self).get_queryset()
        queryset = self._select_related(queryset)
        return self._search(queryset)

    def get_context_data(self, **kwargs):
        context = super(ModelListView, self).get_context_data(**kwargs)
        context.update({
            'columns': self.columns,
            'link_columns': self.link_columns or self.columns[:1],
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
