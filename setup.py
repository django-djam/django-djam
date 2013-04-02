from setuptools import setup, find_packages


setup(
    name="django-djam",
    version='0.1.0',
    maintainer='Stephen Burrows',
    maintainer_email='stephen.r.burrows@gmail.com',
    url='https://github.com/django-djam/django-djam',
    license='BSD',
    packages=find_packages(),
    install_requires=[
        'django>=1.5',
        'django-floppyforms>=1.1',
    ],
    extras_require={
        'docs': ['sphinx>=1.1.3'],
        'tests': ['tox>=1.4.2'],
    },
    classifiers=(
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ),
)
