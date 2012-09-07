import urlparse

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, FormView

from djam.views.base import RiffViewMixin


REDIRECT_FIELD_NAME = 'next'


class LoginView(RiffViewMixin, FormView):
    template_name = 'riffs/auth/login.html'
    redirect_field_name = REDIRECT_FIELD_NAME
    form_class = AuthenticationForm

    def dispatch(self, request, *args, **kwargs):
        self.redirect_to = request.GET.get(self.redirect_field_name, '')
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        redirect_to = self.redirect_to
        netloc = urlparse.urlparse(redirect_to)[1]

        # Use default setting if redirect_to is empty
        if not redirect_to:
            redirect_to = self.riff.base_riff.get_default_url()

        # Heavier security check -- don't allow redirection to a different
        # host.
        elif netloc and netloc != self.request.get_host():
            redirect_to = self.riff.base_riff.get_default_url()

        # Okay, security checks complete. Log the user in.
        login(self.request, form.get_user())

        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()

        return HttpResponseRedirect(redirect_to)

    def get_context_data(self, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)
        context.update({
            'redirect_to': self.redirect_to,
            'redirect_field_name': self.redirect_field_name,
            'site': Site.objects.get_current(),
        })
        return context


class LogoutView(RiffViewMixin, TemplateView):
    template_name = 'riffs/auth/logout.html'
    redirect_field_name = REDIRECT_FIELD_NAME

    def get(self, request, *args, **kwargs):
        logout(request)
        self.redirect_to = request.GET.get(self.redirect_field_name)

        if self.redirect_to:
            netloc = urlparse.urlparse(self.redirect_to)[1]
            # Security check -- don't allow redirection to a different host.
            if not (netloc and netloc != request.get_host()):
                return HttpResponseRedirect(self.redirect_to)

        return super(LogoutView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)
        context.update({
            'site': Site.objects.get_current(),
            'redirect_to': self.redirect_to,
            'redirect_field_name': self.redirect_field_name
        })
        return context
