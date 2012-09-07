# Trick django into treating us as an app.
from django.conf.urls.defaults import patterns

from base import Riff

class ModelRiff(Riff):
    list_view = None
    detail_view = None
    delete_view = None
    history_view = None
    
    def get_urls(self):
        urlpatterns = super(SiteRiff, self).get_urls()
        
        def wrap(view):
            return self.as_view(view)
        
        init = self.get_view_kwargs()
        
        urlpatterns += patterns('',
            url(r'^/$',
                wrap(self.list_view.as_view(**init)),
                name='{appname}_{modelname}_list'),
            url(r'^(?P<pk>\w+)/$',
                wrap(self.detail_view.as_view(**init)),
                name='{appname}_{modelname}_change'),
            url(r'^(?P<pk>\w+)/delete/$',
                wrap(self.delete_view.as_view(**init)),
                name='{appname}_{modelname}_delete'),
            url(r'^(?P<pk>\w+)/history/$',
                wrap(self.history_view.as_view(**init)),
                name='{appname}_{modelname}_history'),
        )
        
        return urlpatterns
