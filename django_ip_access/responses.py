from django.http import JsonResponse, HttpResponse
from django.utils.html import escape

def default_deny_handler(request, message, status_code):
    """
    Auto-detect best response type.
    """

    accept = request.headers.get("Accept", "")

    # 1. DRF (only if request is DRF Request)
    try:
        from rest_framework.request import Request
        from rest_framework.response import Response

        if isinstance(request, Request):
            return Response({"detail": message}, status=status_code)
    except ImportError:
        pass

    # 2. JSON clients
    if "application/json" in accept or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {"message": message},
            status=status_code
        )

    # 3. Default Django template / browser
    return HttpResponse(
        escape(message),
        status=status_code,
        content_type="text/html"
    )
