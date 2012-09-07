from django.conf.urls import patterns, include, url

from djam.riffs.admin import admin


urlpatterns = patterns('',
    url(r'^admin/', include(admin.get_urls_tuple())),
)
