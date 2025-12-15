"""
Decorators for IP and hostname-based access control.

Intended usage:

    from django_ip_access.decorators import ip_access_required
"""

from functools import wraps

from django.conf import settings

from .ip_access_middleware import IPAccessMiddleware
from .utils import get_deny_handler


def ip_access_required(route_config=None):
    """
    Decorator to enforce IP/hostname access control on a single view.

    By default, the current request path is used with an "exact" route type.

    Supports:
    - Plain function-based views: `view(request, *args, **kwargs)`
    - Methods on class-based views / DRF APIViews:
      `view(self, request, *args, **kwargs)`
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(*args, **kwargs):
            # Determine whether this is a function view (request is first arg)
            # or a method on a class-based view / APIView (self, request, ...).
            if not args:
                return view_func(*args, **kwargs)

            first_arg = args[0]

            # Heuristic: anything with a META attribute is "request-like".
            if hasattr(first_arg, "META"):
                # Function-based view: (request, *rest)
                request = first_arg
                call_args = args
            elif len(args) >= 2 and hasattr(args[1], "META"):
                # Method on a class-based view: (self, request, *rest)
                request = args[1]
                call_args = args
            else:
                # Fallback: just call the original view; something unusual.
                return view_func(*args, **kwargs)

            middleware = IPAccessMiddleware(get_response=lambda r: r)

            cfg_route = route_config or {
                "pattern": request.path,
                "type": "exact",
            }

            if not middleware._is_access_allowed(request, cfg_route):
                cfg = getattr(settings, "IP_ACCESS_MIDDLEWARE_CONFIG", {})
                handler = get_deny_handler()
                return handler(
                    request=request,
                    message=cfg.get("DENY_MESSAGE", "Access denied"),
                    status_code=cfg.get("DENY_STATUS_CODE", 403),
                )

            return view_func(*call_args, **kwargs)

        return _wrapped_view

    return decorator


