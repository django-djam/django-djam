from django.utils.cache import add_never_cache_headers
from django.views.generic import View


class RiffView(View):
    riff = None
    cacheable = False
    
    def dispatch(self, request, *args, **kwargs):
        self.request = request
        if not self.permission_check():
            return self.get_unauthorized_response()
        
        response = super(RiffView, self).dispatch(request, *args, **kwargs)
        if not self.cacheable:
            add_never_cache_headers(response)
        return response
    
    def permission_check(self):
        self.riff.permission_check(self.request)
    
    def get_unauthorized_response(self):
        return self.riff.get_unauthorized_respnse(self.request)

