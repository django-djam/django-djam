from django.conf.urls import patterns, include, url
from django.contrib.auth.models import User
from djam.riffs.admin import admin
from djam.riffs.models import UserRiff


admin.register_model(User, UserRiff)


urlpatterns = patterns('',
    url(r'^', include('djam.urls')),
)
