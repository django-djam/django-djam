from django.conf.urls import patterns, include, url
from django.contrib.admin import site

import djam
djam.autodiscover()


urlpatterns = patterns('',
    url(r'^admin/', include(site.urls)),
    url(r'^djam/', include(djam.admin.get_urls_tuple())),
)
