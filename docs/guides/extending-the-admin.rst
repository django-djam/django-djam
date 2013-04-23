Extending the Admin
===================

   **Riff** *n.* (in popular music and jazz) A short repeated phrase,
   frequently played over changing chords or used as a background to a
   solo improvisation.

Like a riff is a building block of jazz music, a :class:`.Riff` is the
building block of the Djam admin. Riffs are essentially modular, decoupled
chunks of namespaced functionality which can be attached to the main admin
site. ModelAdmins (and the Django admin site) work on the same principle.
The main difference in ``djam`` is that riffs don't necessarily map
one-to-one to models. There can be multiple registered riffs related to the
same model, and there can be riffs registered which don't relate to any
model at all.

ModelRiffs
----------

We'll start out with :class:`ModelRiffs <.ModelRiff>`, which are essentially analogous to
``ModelAdmins``. Here is how you could set up some basic ModelRiffs:

.. code-block:: python

   # myapp/riffs.py
   from djam.riffs.models import ModelRiff

   from myapp.models import MyModel, MyOtherModel


   class MyModelRiff(ModelRiff):
       model = MyModel


   class MyModelRiff2(ModelRiff):
       model = MyModel
       namespace = 'myapp_mymodel2'
       display_name = 'MyModel 2'
       slug = 'mymodel-2'


   class MyOtherModelRiff(ModelRiff):
       model = MyOtherModel
       use_modeladmin = False


   # Djam looks for this variable during :func:`.autodiscovery <autodiscover>`.
   riffs = [MyModelRiff, MyOtherModelRiff]

Each :class:`.ModelRiff` class has an associated model. If a ModelAdmin has
been registered for that model, the riff will by default inherit a number
of options from that ModelAdmin, unless ``use_modeladmin`` is ``False``.

.. note: :class:`ModelRiffs <.ModelRiff>` can only inherit options; they
         can't inherit most custom functionality.


Autodiscovery
-------------

.. autofunction:: djam.autodiscover


Great, so it can replace the admin.
-----------------------------------

Why yes, it can. But there's also a lot you can do that goes :doc:`beyond the capabilities of Django's admin </guides/beyond-the-admin>`.