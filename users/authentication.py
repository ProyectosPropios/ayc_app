from django.middleware.csrf import CsrfViewMiddleware
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication


class _CSRFCheck(CsrfViewMiddleware):
    def _reject(self, request, reason):
        return reason


def enforce_csrf(request):
    """Exige el token CSRF cuando la autenticación usa cookies."""
    check = _CSRFCheck(lambda request: None)
    reason = check.process_view(request._request, None, (), {})
    if reason:
        raise PermissionDenied("Solicitud bloqueada por CSRF.")


class CookieJWTAuthentication(JWTAuthentication):
    """Acepta JWT tanto en Authorization como en una cookie HTTP-only."""

    cookie_names = ("access_token", "access")

    def authenticate(self, request):
        header = self.get_header(request)
        if header is not None:
            return super().authenticate(request)

        raw_token = next(
            (request.COOKIES.get(name) for name in self.cookie_names if request.COOKIES.get(name)),
            None,
        )
        if raw_token is None:
            return None

        enforce_csrf(request)
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
