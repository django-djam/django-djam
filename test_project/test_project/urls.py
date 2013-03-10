from django.conf.urls import patterns, include, url

import djam
djam.autodiscover()


urlpatterns = patterns('',
    url(r'^admin/', include(djam.admin.get_urls_tuple())),
)
