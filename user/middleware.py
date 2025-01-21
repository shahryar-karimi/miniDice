from django.utils.deprecation import MiddlewareMixin
from .backends import TokenAuthenticationBackend


class TokenAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('token '):
            token = auth_header.split(' ')[1]  # Extract token part
            backend = TokenAuthenticationBackend()
            user = backend.authenticate(request, token=token)
            request.user = user
