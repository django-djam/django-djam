from djam.forms import GFKField, GFKForm
import floppyforms as forms

from test_project.example_app.models import ExampleModel


class HelloWorldForm(forms.Form):
    name = forms.SlugField()


class ExampleModelForm(GFKForm):
    content_object = GFKField(ExampleModel, 'content_object')

    class Meta:
        model = ExampleModel
        exclude = ('content_type', 'object_id')
