from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

urlpatterns = patterns('',
	url(r'^', include('djam.urls')),
	url(r'^', TemplateView.as_view('login.html'))
)
