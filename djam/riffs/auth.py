from django.conf.urls import patterns, url

from djam.riffs.base import Riff

class SiteRiff(Riff):
    login_view = None
    logout_view = None
    verbose_name = 'site'
    
    def get_urls(self):
        urlpatterns = super(SiteRiff, self).get_urls()
        
        def wrap(view):
            return self.as_view(view)
        
        init = self.get_view_kwargs()
        
        urlpatterns += patterns('',
            url(r'^logout/$',
                wrap(self.logout_view.as_view(**init)),
                name='logout'),
            url(r'^login/$',
                wrap(self.logout_view.as_view(**init)),
                name='login'),
        )
        
        return urlpatterns
    
    def has_permission(self, request):
        if not request.user.is_active and not request.user.is_authenticated():
            return False
        return super(SiteRiff, self).has_permission(request)
