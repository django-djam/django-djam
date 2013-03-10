from __future__ import unicode_literals

from django.contrib.admin.util import flatten_fieldsets
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
        context.update(verbose_name=self.model._meta.verbose_name)
        return context


class ModelListView(ModelRiffMixin, ListView):
    template_name_suffix = 'list'


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
