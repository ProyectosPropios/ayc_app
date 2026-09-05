class PrivateResponseHeadersMiddleware:
    """Evita que respuestas privadas de la API queden en cachés del navegador."""

    PRIVATE_PREFIXES = ("/api/", "/admin/")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith(self.PRIVATE_PREFIXES):
            response["Cache-Control"] = "no-store, max-age=0"
            response["Pragma"] = "no-cache"
        return response
