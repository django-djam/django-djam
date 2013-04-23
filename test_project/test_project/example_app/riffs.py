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
