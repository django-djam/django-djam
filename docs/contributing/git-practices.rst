Git practices
=============

We follow the `same guidelines for using git (and github) as Django <https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/working-with-git/>`_, with one exception: we prefer ticket branches be named ``ticket/xxxx``.

Occasionally, devs will start a release branch for Djam. This branch will be named according to the minor release number, and will be used to track bugfixes for that release. Release branches will occasionally be merged back into master. When a release is made, it will be tagged with the full version number.
