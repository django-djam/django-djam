Contributing to Djam
====================

Coding style
------------

* Unless otherwise specified, follow `PEP 8`_. Since we're a new
  project, there shouldn't be any cases (apart from those outlined
  here) where you need to instead conform to surrounding code.
* Use four spaces for indentation.
* In docstrings, use "action words". For example, "Calculates the number
  of apples" rather than "Calculate the number of apples".
* Empty lines should not contain indentation.
* Always use absolute imports. They're easier to debug and are 3.0
  forwards-compatible.
* Be sure to include ``from __future__ import unicode_literals`` at
  the top of any file that uses strings.

.. _PEP 8: http://www.python.org/dev/peps/pep-0008/


Git practices
-------------

We follow the `same guidelines for using git (and github) as Django <https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/working-with-git/>`_, with one exception: we prefer ticket branches
be named ``ticket/xxxx``.
