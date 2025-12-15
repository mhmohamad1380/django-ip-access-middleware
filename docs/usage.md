## Usage

### Protecting routes via middleware configuration

Configure which routes should be protected in your `settings.py` using
`IP_ACCESS_MIDDLEWARE_CONFIG`:

```python
import os

IP_ACCESS_MIDDLEWARE_CONFIG = {
    "DENY_MESSAGE": "Access denied",
    "DENY_STATUS_CODE": 403,
    # "DENY_RESPONSE_HANDLER": "myapp.security.custom_deny_handler",  # optional
    "routes": [
        {
            "pattern": r"^/admin/.*",
            "type": "regex",
        },
        {
            "pattern": "/api/",
            "type": "startswith",
        },
        {
            "pattern": ".json",
            "type": "endswith",
        },
        {
            "pattern": "/api/secure/",
            "type": "exact",
        },
    ],
    "kubernetes_network_range": os.getenv("KUBERNETES_NETWORK_RANGE", ""),
    "pod_ip": os.getenv("POD_IP", ""),
}

ALLOWED_HOSTNAMES_ENV = os.getenv("ALLOWED_HOSTNAMES", "")
```

### Managing granted IPs

Use the Django admin or the `GrantedIP` model to define allowed IPs:

```python
from django_ip_access.models import GrantedIP

# Single IP
GrantedIP.objects.create(
    ip_address="192.168.1.100",
    description="Development server",
    is_active=True,
)

# CIDR range
GrantedIP.objects.create(
    ip_address="10.0.0.0/24",
    description="Internal network",
    is_active=True,
)
```

### Opt-in protection with mixins and decorators

#### Class-based views

```python
from django.views.generic import TemplateView
from django_ip_access.mixins import IPAccessMixin


class SecureDashboardView(IPAccessMixin, TemplateView):
    template_name = "secure_dashboard.html"

    # Optional: customise route matching
    # ip_access_route_config = {
    #     "pattern": "/dashboard/",
    #     "type": "startswith",
    # }
```

#### Function-based views

```python
from django_ip_access.decorators import ip_access_required


@ip_access_required()
def secure_view(request):
    ...


@ip_access_required(route_config={"pattern": "/api/", "type": "startswith"})
def secure_api_view(request):
    ...
```


