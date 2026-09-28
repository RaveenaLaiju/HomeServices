from django.utils.deprecation import MiddlewareMixin

class SessionCookieSwitcherMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith("/admin"):
            request.session_cookie_name = "sessionid_admin"
        elif request.path.startswith("/provider"):
            request.session_cookie_name = "sessionid_provider"
        else:
            request.session_cookie_name = "sessionid_customer"
