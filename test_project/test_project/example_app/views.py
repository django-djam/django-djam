from django.http import HttpResponseRedirect
from djam.views.generic import FormView, TemplateView

from test_project.example_app.forms import HelloWorldForm


class HelloView(FormView):
    form_class = HelloWorldForm
    template_name = 'djam/form.html'

    def form_valid(self, form):
        url = self.riff.reverse('hello_finished',
                                slug=form.cleaned_data['name'])
        return HttpResponseRedirect(url)


class HelloFinishedView(TemplateView):
    template_name = 'example_app/hello.html'

    def get_crumbs(self):
        crumbs = super(HelloFinishedView, self).get_crumbs()
        return crumbs + [(None, self.kwargs['slug'])]
