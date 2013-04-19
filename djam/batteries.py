from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.models import User
from django.conf.urls import patterns, url

from djam.riffs.models import ModelRiff
from djam.views.generic import UpdateView
from djam.views.models import ModelRiffMixin


class UserPasswordView(ModelRiffMixin, UpdateView):
    form_class = AdminPasswordChangeForm
    template_name = 'djam/models/auth/user/password-change.html'

    def get_success_url(self):
        return self.riff.reverse('update', pk=self.object.pk)

    def has_permission(self, request):
        return self.riff.has_change_permission(request)

    def get_form_kwargs(self):
        kwargs = super(UserPasswordView, self).get_form_kwargs()
        kwargs['user'] = kwargs.pop('instance')
        return kwargs

    def get_crumbs(self):
        crumbs = super(UserPasswordView, self).get_crumbs()
        crumbs += [
            (self.riff.reverse('update', pk=self.object.pk),
             unicode(self.object)),
            (None, 'Change password'),
        ]
        return crumbs


class UserRiff(ModelRiff):
    model = User

    def get_password_change_kwargs(self):
        return self.get_view_kwargs()

    def get_extra_urls(self):
        urlpatterns = super(UserRiff, self).get_extra_urls()
        urlpatterns += patterns('',
            url(r'^(?P<pk>\w+)/password/',
                UserPasswordView.as_view(**self.get_password_change_kwargs()),
                name='password-change'),
        )
        return urlpatterns


riffs = [UserRiff]
