from django import forms


class HelloWorldForm(forms.Form):
    name = forms.SlugField()
