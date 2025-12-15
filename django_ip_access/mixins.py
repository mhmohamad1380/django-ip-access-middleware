class IPAccessMixin:
    """
    Opt-in IP/hostname access control for class-based views (Django & DRF).

    By default, this applies the same rules as `IPAccessMiddleware` to the
    current request path only (using an "exact" route pattern).

    You can override `ip_access_route_config` on your view to customise the
    route configuration that is passed to the underlying middleware logic.
    """

    #: Optional override to control how the route is matched.
    #: Example:
    #: ip_access_route_config = {"pattern": "/api/", "type": "startswith"}
    ip_access_route_config = None

    def dispatch(self, request, *args, **kwargs):
        from django.conf import settings
        from .ip_access_middleware import IPAccessMiddleware
        from .utils import get_deny_handler

        # Reuse the same core logic from the middleware.
        middleware = IPAccessMiddleware(get_response=lambda r: r)

        # Default route configuration: only this exact path.
        route_config = self.ip_access_route_config or {
            "pattern": request.path,
            "type": "exact",
        }

        if not middleware._is_access_allowed(request, route_config):
            cfg = getattr(settings, "IP_ACCESS_MIDDLEWARE_CONFIG", {})
            handler = get_deny_handler()
            return handler(
                request=request,
                message=cfg.get("DENY_MESSAGE", "Access denied"),
                status_code=cfg.get("DENY_STATUS_CODE", 403),
            )

        return super().dispatch(request, *args, **kwargs)

