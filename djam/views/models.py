from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from djam.views.base import RiffViewMixin


class ModelRiffMixin(RiffViewMixin):
    template_name_suffix = None

    def get_template_names(self):
        if self.template_name:
            return [self.template_name]
        
        applabel = self.model._meta.app_label
        slug = self.riff.slug
        
        return ['djam/{applabel}/{modelname}/{suffix}.html'.format(suffix=self.template_name_suffix, applabel=applabel, modelname=slug),
                'djam/{applabel}/{suffix}.html'.format(suffix=self.template_name_suffix, applabel=applabel),
                'djam/{suffix}.html'.format(suffix=self.template_name_suffix),]

class ModelListView(ModelRiffMixin, ListView):
    template_name_suffix = 'change_list'

class ModelCreateView(ModelRiffMixin, CreateView):
    template_name_suffix = 'change_form'
    
    def get_success_url(self):
        format_params = {
            'appname': self.model._meta.app_label,
            'modelname': self.riff.slug
        }
        
        return self.reverse('{appname}_{modelname}_change'.format(**format_params), pk=self.object.pk)

class ModelDetailView(ModelRiffMixin, UpdateView):
    template_name_suffix = 'change_form'

class ModelDeleteView(ModelRiffMixin, DeleteView):
    template_name_suffix = 'delete'
    
    def get_success_url(self):
        return self.riff.get_default_url()

class ModelHistoryView(ModelRiffMixin, ListView):
    template_name_suffix = 'history'

