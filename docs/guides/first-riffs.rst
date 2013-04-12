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
       use_modeladmin = False


   riffs = [MyModelRiff, MyOtherModelRiff]


.. code-block:: python

   # myproject/urls.py
   from django.conf.urls import patterns, include, urls

   import djam
   djam.autodiscover()

   urlpatterns = patterns('',
       url(r'^admin/', include(djam.admin.get_urls_tuple())),
   )

If you use runserver and navigate to ``/admin/``, you'll be able to
add, edit, and delete models! (Assuming you have the correct
permissions, of course.)


Autodiscovery
-------------

.. autofunction:: djam.autodiscover


ModelRiffs automatically inherit from ModelAdmins
-------------------------------------------------

Each :class:`ModelRiff` class has an associated model. If a ModelAdmin has
been registered for that model, the riff will by default inherit a number
of options from that ModelAdmin.

However, :class:`ModelRiffs <ModelRiff>` can only inherit options; they can't inherit most custom
functionality.
