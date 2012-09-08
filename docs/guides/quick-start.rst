Quick Start
===========

For your convenience, Djam comes with a fully-functional example project
which can be used in a development environment to experiment with and
test the project.

.. warning:: The example project uses ``DEBUG = True`` and a secret key
             which is freely available on the internet. Using this
             project unaltered is **extremely insecure** and only fit
             for a development environment.

Use virtualenv
--------------

If you already use virtualenv_, you can skip this section.

.. _virtualenv: http://virtualenv.org/

Okay, you're still here. Virtualenv is a great thing. You should be
using it.

First, make sure you have pip_ installed. Pip is an improved package management tool for python.

.. _pip: http://www.pip-installer.org/

.. code-block:: bash

   $ sudo easy_install pip
   $ sudo pip install virtualenv

.. note:: Depending on how your system is set up, you may not need
          to use sudo for this step.

Now let's set up your virtualenv:

.. code-block:: bash

   $ mkdir ~/envs
   $ cd ~/envs
   $ virtualenv myenv
   $ cd myenv
   $ source bin/activate

Now that the virtualenv has been activated, python packages will be
installed inside the virtualenv instead of system-wide. That way,
changes to the system packages won't suddenly break whatever is running
inside the virtual environment.

Installing djam
---------------

So you've created and activated a virtualenv. Time to install djam!

.. code-block:: bash

   $ pip install -e git+git://github.com/pculture/django-djam.git#egg=django-djam --no-deps
   $ cd src/django-djam/example_djam_project
   $ pip install -r requirements.txt
   $ ./manage.py runserver

Adding djam to a larger project
-------------------------------

Since djam is just an admin, there's not much to do when all you have is
the example project. If you're adding djam to a larger project, all you
have to do is:

* Make sure ``"djam"`` is in the ``INSTALLED_APPS``.
* Make sure ``"django.core.context_processors.request"`` is in the TEMPLATE_CONTEXT_PROCESSORS. (See the example project settings for an example.)
* :doc:`Make your first riffs! </guides/first-riffs>`
