from __future__ import unicode_literals
import urlparse

from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _

from djam.views.generic import FormView, TemplateView


REDIRECT_FIELD_NAME = 'next'


class LoginView(FormView):
    template_name = 'djam/auth/login.html'
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

    def get_crumbs(self):
        return [
            (None, self.riff.base_riff.display_name),
            (None, _('Login')),
        ]


class LogoutView(TemplateView):
    template_name = 'djam/auth/logout.html'
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
        context = super(LogoutView, self).get_context_data(**kwargs)
        context.update({
            'site': Site.objects.get_current(),
            'redirect_to': self.redirect_to,
            'redirect_field_name': self.redirect_field_name
        })
        return context

    def get_crumbs(self):
        return [
            (None, self.riff.base_riff.display_name),
            (None, _('Logout')),
        ]


class PasswordChangeView(FormView):
    form_class = PasswordChangeForm
    template_name = 'djam/auth/password-change.html'

    def get_form_kwargs(self):
        kwargs = super(PasswordChangeView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return super(PasswordChangeView, self).form_valid(form)

    def get_success_url(self):
        return self.riff.base_riff.get_default_url()

    def get_crumbs(self):
        crumbs = super(PasswordChangeView, self).get_crumbs()
        crumbs = crumbs[:-1] + [(None, _('Change password'))]
        return crumbs
