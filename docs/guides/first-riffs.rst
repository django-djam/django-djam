First Riffs
===========

   **Riff** *n.* (in popular music and jazz) A short repeated phrase,
   frequently played over changing chords or used as a background to a
   solo improvisation.

Like a riff is a building block of jazz music, a :class:`Riff` is the
building block of the Djam admin. Riffs are tied together in a tree
structure; they have knowledge of their parents, their children, and the
tree root. The url for the base of each riff is determined by its parent.
Each riff creates a namespace for its views.

Setting up a basic admin
------------------------

Here's an example of how you could set up your admin using djam:

.. code-block:: python

   # myapp/riffs.py
   from djam.riffs.models import ModelRiff

   from myapp.models import MyModel, MyOtherModel


   class MyModelRiff(ModelRiff):
       model = MyModel

   class MyOtherModelRiff(ModelRiff):
       model = MyOtherModel


.. code-block:: python

   # myproject/urls.py
   from django.conf.urls import patterns, include, urls

   from djam.riffs.admin import AdminRiff

   from myapp.riffs import MyModelRiff, MyOtherModelRiff


   class MyProjectAdminRiff(AdminRiff):
       riff_classes = AdminRiff.riff_classes + (MyModelRiff, MyOtherModelRiff,)

   admin = MyProjectAdminRiff()

   urlpatterns = patterns('',
       url(r'^admin/', include(admin.get_urls_tuple())),
   )

If you use runserver and navigate to ``/admin/``, you'll be able to add, edit, and delete models! (Assuming you have the correct permissions, of course.)
