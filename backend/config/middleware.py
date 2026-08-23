class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # X-Content-Type-Options
        response['X-Content-Type-Options'] = 'nosniff'

        # X-Frame-Options
        response['X-Frame-Options'] = 'DENY'

        # Content-Security-Policy (basic)
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "img-src 'self' data: https:; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "script-src 'self' 'unsafe-inline' https://code.jquery.com; "
            "connect-src 'self'"
        )

        return response