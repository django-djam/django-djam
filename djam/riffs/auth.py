from django.conf.urls import patterns, url

from djam.riffs.base import Riff
from djam.views.auth import LoginView, LogoutView


class AuthRiff(Riff):
    login_view = LoginView
    logout_view = LogoutView
    verbose_name = 'Auth'

    def get_login_kwargs(self):
        return self.get_view_kwargs()

    def get_logout_kwargs(self):
        return self.get_view_kwargs()
    
    def get_urls(self):
        urlpatterns = super(AuthRiff, self).get_urls()
        
        def wrap(view):
            return self.wrap_view(view)
        
        urlpatterns += patterns('',
            url(r'^logout/$',
                wrap(self.logout_view.as_view(**self.get_logout_kwargs())),
                name='logout'),
            url(r'^login/$',
                wrap(self.login_view.as_view(**self.get_login_kwargs())),
                name='login'),
        )
        
        return urlpatterns
    
    def has_permission(self, request):
        # Login/logout don't care whether you're authenticated.
        return True
