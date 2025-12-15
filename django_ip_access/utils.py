# django_ip_access/utils.py

from django.conf import settings
from django.utils.module_loading import import_string

DEFAULT_HANDLER = "django_ip_access.responses.default_deny_handler"

def get_deny_handler():
    cfg = getattr(settings, "IP_ACCESS_MIDDLEWARE", {})
    path = cfg.get("DENY_RESPONSE_HANDLER", DEFAULT_HANDLER)
    return import_string(path)
