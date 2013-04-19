from djam.views.generic import RedirectView


class DefaultRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, **kwargs):
        return self.riff.get_default_url()
