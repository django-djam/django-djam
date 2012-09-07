from django.conf.urls import patterns, include, url

from djam.riffs.auth import AuthRiff


urlpatterns = patterns('',
    url(r'^', include(AuthRiff().get_urls(),
                      namespace='auth',
                      app_name='djam')),
)
