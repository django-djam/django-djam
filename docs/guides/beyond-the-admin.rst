Beyond ``django.contrib.admin``
===============================

A Model-less Riff
-----------------

Here's an example of a riff which is simple to implement in Djam, but which
in Django's admin would require (at the very least) overriding several base
templates and using a custom AdminSite subclass. This code is taken directly from the test project's example app.


.. code-block:: python

   # example_app/riffs.py
   from django.conf.urls import patterns, url
   from djam.riffs.base import Riff

   from test_project.example_app.views import HelloView, HelloFinishedView


   class HelloRiff(Riff):
       display_name = "Hello"
 
       def get_extra_urls(self):
           return patterns('',
               url(r'^$',
                   HelloView.as_view(**self.get_view_kwargs()),
                   name='hello'),
               url(r'^(?P<slug>[\w-]+)/$',
                   HelloFinishedView.as_view(**self.get_view_kwargs()),
                   name='hello_finished'),
           )

       def get_default_url(self):
           return self.reverse('hello')


   riffs = [HelloRiff]

Essentially, this riff has one view which asks a user for their name (a
slug) and another view which says "Hello <name>". It doesn't use any
models. Or more to the point, it doesn't provide a CRUD interface for
interacting with a particular model.

.. code-block:: python

   # example_app/forms.py
   from django import forms


   class HelloWorldForm(forms.Form):
       name = forms.SlugField()

.. code-block:: python

   # example_app/views.py
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

The notable difference here is that we're importing our generic views from
:mod:`djam.views.generic` rather than :mod:`django.views.generic`. These
views have some riff-specific functionality, including providing the riff
itself – and breadcrumbs for navigation – to the template context.

.. code-block:: html+django

   {# example_app/templates/example_app/hello.html #}
   {% extends 'djam/__base.html' %}

   {% load webdesign djam %}

   {% block main %}
       <h1>Hello, {{ slug }}!</h1>

       {% lorem 3 p random %}

       <a href="{% riff_url riff 'hello' %}" class='btn btn-success btn-large'>Once more!</a>
   {% endblock %}

In this template, you can see the ``{% riff_url %}`` template tag
being used. It reverses the given view name (``'hello'``) within the
namespace of the given riff (in this case the current riff).

And that's it!
