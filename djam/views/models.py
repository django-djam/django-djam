from django.views.generic import ListView, DetailView

from djam.views.base import RiffView


class ModelRiffView(RiffView):
    template_suffix = None

    def get_template_names(self):
        if self.template_name:
            return [self.template_name]
        
        applabel = self.model._meta.app_label
        slug = self.riff.slug
        
        return ['djamin/{applabel}/{modelname}/{suffix}.html'.format(suffix=self.template_suffix, applabel=applabel, modelname=slug),
                'djamin/{applabel}/{suffix}.html'.format(suffix=self.template_suffix, applabel=applabel),
                'djamin/{suffix}.html'.format(suffix=self.template_suffix),]

class ModelListView(ModelRiffView, ListView):
    template_suffix = 'change_list'

class ModelDetailView(ModelRiffView, DetailView):
    template_suffix = 'change_form'

class ModelDeleteView(ModelRiffView, DetailView):
    template_suffix = 'delete'

class ModelHistoryView(ModelRiffView, ListView):
    template_suffix = 'history'

