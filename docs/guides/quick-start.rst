Quick Start
===========

Trying out djam is easy, especially if you're already using ``django.contrib.admin``. First, just install it.

.. code-block:: bash

   $ pip install -e git+git://github.com/pculture/django-djam.git#egg=django-djam

Djam requires Django 1.5+ and Django-Floppyforms 1.1+.

``urls.py``
-----------

Next, go into the urls.py file for your project. There is probably something there along these lines::

   from django.contrib import admin
   admin.autodiscover()

   urlpatterns = patterns('',
       url(r'^admin/', include(admin.site.urls)),
   )

All you need to do here is change it to look more like the following::

   import djam
   djam.autodiscover()

   urlpatterns = patterns('',
       url(r'^admin/', include(djam.admin.urls)),
   )

.. note:: It's also entirely possible to run ``djam`` and
          ``django.contrib.admin`` side-by-side.

``settings.py``
---------------

Now go into your settings file. Make sure that ``"djam"`` is somewhere
in your ``INSTALLED_APPS``, and that ``"django.core.context_processors.request"`` is in your ``TEMPLATE_CONTEXT_PROCESSORS``.

Congratulations!
----------------

You're now using djam. It won't capture all the custom functionality
of the ModelAdmins you already have installed, but we do support transferring most of the basic ModelAdmin options.

Once you've had a chance to play with your auto-generated djam admin, go ahead and :doc:`make your first custom riffs! </guides/first-riffs>`
