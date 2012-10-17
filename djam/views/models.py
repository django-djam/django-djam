from __future__ import unicode_literals

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.utils.translation import ugettext_lazy as _

from djam.views.base import RiffViewMixin


class ModelRiffMixin(RiffViewMixin):
    template_name_suffix = None

    def get_template_names(self):
        if self.template_name:
            return [self.template_name]
        
        applabel = self.model._meta.app_label
        slug = self.riff.slug
        
        return ['djam/models/{applabel}/{modelname}/{suffix}.html'.format(suffix=self.template_name_suffix, applabel=applabel, modelname=slug),
                'djam/models/{applabel}/{suffix}.html'.format(suffix=self.template_name_suffix, applabel=applabel),
                'djam/models/{suffix}.html'.format(suffix=self.template_name_suffix),]

    def get_context_data(self, **kwargs):
        context = super(ModelRiffMixin, self).get_context_data(**kwargs)
        context.update(verbose_name=self.model._meta.verbose_name)
        return context

class ModelListView(ModelRiffMixin, ListView):
    template_name_suffix = 'list'

class ModelCreateView(ModelRiffMixin, CreateView):
    template_name_suffix = 'create'
    
    def get_success_url(self):
        return self.riff.reverse('update', pk=self.object.pk)

    def get_context_data(self, **kwargs):
        context = super(ModelCreateView, self).get_context_data(**kwargs)
        context.update(page_title=_('Add a {0}'.format(self.model._meta.verbose_name)))
        return context

class ModelUpdateView(ModelRiffMixin, UpdateView):
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

