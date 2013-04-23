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
          ``django.contrib.admin`` side-by-side, if you want to
          compare the two. The test project does it!

``settings.py``
---------------

Now go into your settings file.

First, make sure that ``djam`` and ``floppyforms`` are somewhere in
your ``INSTALLED_APPS``. For example::

  INSTALLED_APPS = (
      'django.contrib.auth',
      'django.contrib.contenttypes',
      'django.contrib.sessions',
      'django.contrib.sites',
      'django.contrib.messages',
      'django.contrib.staticfiles',

      # Other apps...
      'djam',
      'floppyforms',
  )

Now make sure that ``django.core.context_proocessors.request`` is in your ``TEMPLATE_CONTEXT_PROCESSORS``. If you just add it to Django's defaults, you'll get::

  TEMPLATE_CONTEXT_PROCESSORS = (
      "django.contrib.auth.context_processors.auth",
      "django.core.context_processors.debug",
      "django.core.context_processors.i18n",
      "django.core.context_processors.media",
      "django.core.context_processors.static",
      "django.core.context_processors.tz",
      "django.contrib.messages.context_processors.messages",
      "django.core.context_processors.request",
  )

Congratulations!
----------------

You're now using djam. Go ahead and log in; have a look around. All
of the ``ModelAdmins`` you registered with ``django.contrib.admin``
should already be showing up on the dashboard. Whenever you feel
ready, you can move on to :doc:`/guides/extending-the-admin` and find out
why that is.
