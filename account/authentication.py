#account.authentication.py

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # First, try to authenticate using the standard method (from headers)
        auth_result = super().authenticate(request)

        if auth_result is not None:
            return auth_result

        # If no authentication was found in headers, check cookies
        token = request.COOKIES.get('jwt_access')
        if not token:
            return None  # No token found in cookies

        # Validate the token
        validated_token = self.get_validated_token(token)

        return self.get_user(validated_token), validated_token