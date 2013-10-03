from django.contrib.auth.forms import (AdminPasswordChangeForm,
                                       UserCreationForm,
                                       UserChangeForm)
from django.contrib.auth.models import User
from django.conf.urls import patterns, url
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
import floppyforms

from djam.riffs.auth import AuthRiff
from djam.riffs.dashboard import DashboardRiff
from djam.riffs.models import ModelRiff
from djam.views.generic import FormView
from djam.views.models import ModelRiffMixin


class FloppyUserCreationForm(UserCreationForm):
    username = floppyforms.RegexField(
        label=_("Username"),
        max_length=30,
        regex=r'^[\w.@+-]+$',
        help_text=_("Required. 30 characters or fewer. Letters, digits and "
                    "@/./+/-/_ only."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")})
    password1 = floppyforms.CharField(label=_("Password"),
                                      widget=floppyforms.PasswordInput)
    password2 = floppyforms.CharField(
        label=_("Password confirmation"),
        widget=floppyforms.PasswordInput,
        help_text=_("Enter the same password as above, for verification."))


class FloppyUserChangeForm(UserChangeForm):
    username = floppyforms.RegexField(
        label=_("Username"),
        max_length=30,
        regex=r"^[\w.@+-]+$",
        help_text=_("Required. 30 characters or fewer. Letters, digits and "
                      "@/./+/-/_ only."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")})


class UserPasswordView(ModelRiffMixin, FormView):
    form_class = AdminPasswordChangeForm
    template_name = 'djam/models/auth/user/password-change.html'
    model = User

    def get_success_url(self):
        return self.riff.reverse('update', kwargs={'pk': self.kwargs['pk']})

    def has_permission(self, request):
        return self.riff.has_change_permission(request)

    def get_form_kwargs(self):
        kwargs = super(UserPasswordView, self).get_form_kwargs()
        try:
            self.object = User.objects.get(pk=self.kwargs['pk'])
        except (User.DoesNotExist, KeyError):
            raise Http404
        kwargs['user'] = self.object
        return kwargs

    def form_valid(self, form):
        form.save()
        return super(UserPasswordView, self).form_valid(form)

    def get_crumbs(self):
        crumbs = super(UserPasswordView, self).get_crumbs()
        crumbs += [
            (self.riff.reverse('update', kwargs={'pk': self.kwargs['pk']}),
             unicode(self.object)),
            (None, 'Change password'),
        ]
        return crumbs


class UserRiff(ModelRiff):
    model = User

    create_kwargs = {
        'form_class': FloppyUserCreationForm,
    }

    update_kwargs = {
        'form_class': FloppyUserChangeForm,
        'fieldsets': (
            (None, {'fields': ('username', 'password')}),
            (_('Personal info'),
             {'fields': ('first_name', 'last_name', 'email')}),
            (_('Permissions'),
             {'fields': ('is_active', 'is_superuser',
                         'groups', 'user_permissions')}),
            (_('Important dates'),
             {'fields': ('last_login', 'date_joined')}),
        ),
    }

    def get_password_change_kwargs(self):
        return {'riff': self}

    def get_extra_urls(self):
        urlpatterns = super(UserRiff, self).get_extra_urls()
        urlpatterns += patterns('',
            url(r'^(?P<pk>\w+)/password/',
                UserPasswordView.as_view(**self.get_password_change_kwargs()),
                name='password-change'),
        )
        return urlpatterns


riffs = [AuthRiff, DashboardRiff, UserRiff]
