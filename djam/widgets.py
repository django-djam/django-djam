from django.template import loader
from floppyforms import Widget


class AddWrapper(Widget):
    template_name = 'floppyforms/addwrapper.html'

    def __init__(self, widget, riff):
        self.widget = widget
        self.riff = riff
        super(AddWrapper, self).__init__()

    def get_context(self, name, value, attrs=None, **kwargs):
        attrs = attrs or {}
        context = {
            'rendered': self.widget.render(name, value, attrs, **kwargs),
            'riff': self.riff,
        }
        context['attrs'] = self.build_attrs(attrs)
        return context

    def render(self, name, value, attrs=None, **kwargs):
        context = self.get_context(name, value, attrs, **kwargs)
        return loader.render_to_string(
            self.template_name,
            dictionary=context,
            context_instance=None)
