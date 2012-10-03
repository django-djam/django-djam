from django.conf.urls import patterns, include, url
from django.contrib.auth.models import User
from djam.riffs.admin import admin


admin.register_model(User)


urlpatterns = patterns('',
    url(r'^', include('djam.urls')),
)
