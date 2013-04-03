from __future__ import unicode_literals

from django.conf.urls import patterns, url
from django.utils.translation import ugettext_lazy as _

from djam.riffs.base import Riff
from djam.views.auth import LoginView, LogoutView, PasswordChangeView


class AuthRiff(Riff):
    login_view = LoginView
    logout_view = LogoutView
    password_change_view = PasswordChangeView
    display_name = _('Auth')

    def get_login_kwargs(self):
        return self.get_view_kwargs()

    def get_logout_kwargs(self):
        return self.get_view_kwargs()

    def get_password_change_kwargs(self):
        return self.get_view_kwargs()

    def get_urls(self):
        urlpatterns = super(AuthRiff, self).get_urls()

        urlpatterns += patterns('',
            url(r'^logout/$',
                self.wrap_view(self.logout_view.as_view(**self.get_logout_kwargs())),
                name='logout'),
            url(r'^login/$',
                self.wrap_view(self.login_view.as_view(**self.get_login_kwargs())),
                name='login'),
            url(r'^password/change/$',
                self.wrap_view(self.password_change_view.as_view(**self.get_password_change_kwargs())),
                name='password-change'),
        )

        return urlpatterns

    def has_permission(self, request):
        # Login/logout don't care whether you're authenticated.
        return True

    def get_default_url(self):
        if self.parent is not None:
            return self.parent.get_default_url()
        return self.reverse('login')
