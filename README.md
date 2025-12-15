# Django IP Access Control Middleware

A Django middleware for IP and hostname-based access control with support for:
- IP addresses and CIDR ranges from database
- Hostname matching from environment variables
- Automatic same-network detection for Kubernetes
- Route-based access control with regex, exact, startswith, endswith patterns

## Features

- **Database-driven IP control**: Store granted IP addresses and CIDR ranges in the database
- **Environment-based hostnames**: Configure allowed hostnames via environment variables
- **Kubernetes support**: Automatic same-network detection for pods in the same cluster
- **Flexible route matching**: Support for regex, exact match, startswith, and endswith patterns
- **Priority-based access control**: 
  1. Same network detection (highest priority - allows immediately)
  2. Hostname matching (from environment variables)
  3. IP checking (from database)

## Installation

```bash
pip install django-ip-access-middleware
```

Or install from source:

```bash
pip install -e .
```

## Quick Start

### 1. Add to INSTALLED_APPS

Add `django_ip_access` to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    # ... other apps
    'django_ip_access',
]
```

### 2. Add Middleware

Add the middleware to your `MIDDLEWARE` list in `settings.py`:

```python
MIDDLEWARE = [
    # ... other middleware
    'django_ip_access.middleware.IPAccessMiddleware',
    # ... other middleware
]
```

### 3. Run Migrations

Create and run migrations for the database model:

```bash
python manage.py makemigrations django_ip_access
python manage.py migrate django_ip_access
```

### 4. Configure Routes

Configure which routes should be protected in `settings.py`:

```python
IP_ACCESS_MIDDLEWARE_CONFIG = {
    "DENY_MESSAGE": "Access denied",
    "DENY_STATUS_CODE": 403,
    # optional override
    # "DENY_RESPONSE_HANDLER": "myapp.security.custom_deny_handler",
    'routes': [
        {
            'pattern': r'^/admin/.*',  # regex pattern
            'type': 'regex',
        },
        {
            'pattern': '/api/',  # starts with
            'type': 'startswith',
        },
        {
            'pattern': '.json',  # ends with
            'type': 'endswith',
        },
        {
            'pattern': '/api/secure/',  # exact match
            'type': 'exact',
        },
    ],
    # Optional: Kubernetes network configuration
    'kubernetes_network_range': os.getenv('KUBERNETES_NETWORK_RANGE', ''),  # e.g., '10.244.0.0/16'
    'pod_ip': os.getenv('POD_IP', ''),  # Kubernetes pod IP
}

# Environment variable for allowed hostnames (comma-separated)
ALLOWED_HOSTNAMES_ENV = os.getenv('ALLOWED_HOSTNAMES', '')
# Example: ALLOWED_HOSTNAMES="*.example.com,api.example.com,*.subdomain.com"
```

### 5. Add Granted IPs

Use Django admin or create `GrantedIP` objects to allow IP addresses:

```python
from django_ip_access.models import GrantedIP

# Add a single IP
GrantedIP.objects.create(
    ip_address='192.168.1.100',
    description='Development server',
    is_active=True
)

# Add an IP range (CIDR)
GrantedIP.objects.create(
    ip_address='10.0.0.0/24',
    description='Internal network',
    is_active=True
)
```

## Configuration

### Route Types

- **regex**: Match using regular expressions
- **exact**: Exact path match
- **startswith**: Match if path starts with pattern
- **endswith**: Match if path ends with pattern

### Environment Variables

- `ALLOWED_HOSTNAMES`: Comma-separated list of allowed hostnames (supports wildcards like `*.example.com`)
- `POD_IP`: Kubernetes pod IP (optional, for explicit network detection)
- `KUBERNETES_NETWORK_RANGE`: Kubernetes network range (optional, e.g., `10.244.0.0/16`)

### Same Network Detection

The middleware automatically detects if the client IP is on the same network as the server:
- Checks if both IPs are private IPs on the same subnet
- Works automatically without configuration
- Highest priority - if same network is detected, access is allowed immediately

## Usage Examples

### Protect Admin Routes

```python
IP_ACCESS_MIDDLEWARE_CONFIG = {
    'routes': [
        {
            'pattern': r'^/admin/.*',
            'type': 'regex',
        },
    ],
}
```

### Protect API Routes

```python
IP_ACCESS_MIDDLEWARE_CONFIG = {
    'routes': [
        {
            'pattern': '/api/',
            'type': 'startswith',
        },
    ],
}
```

### Allow Hostnames from Environment

Set environment variable:
```bash
export ALLOWED_HOSTNAMES="*.example.com,api.example.com"
```

## Opt-in usage with mixins and decorators

Sometimes you don’t want to install the middleware globally, but instead
protect only specific views. This package provides a mixin and a decorator
that reuse the exact same access-control logic as the middleware.

### Django class-based views

```python
from django.views.generic import TemplateView
from django_ip_access.mixins import IPAccessMixin


class SecureDashboardView(IPAccessMixin, TemplateView):
    template_name = "secure_dashboard.html"

    # Optional: customise how the route is matched
    # ip_access_route_config = {
    #     "pattern": "/dashboard/",
    #     "type": "startswith",
    # }
```

### Django function-based views

```python
from django_ip_access.decorators import ip_access_required


@ip_access_required()  # default: protect this exact path only
def secure_view(request):
    ...


@ip_access_required(route_config={"pattern": "/api/", "type": "startswith"})
def secure_api_view(request):
    ...
```

### Django REST framework: generic views & APIView

`IPAccessMixin` works out of the box with DRF generic views and `APIView`,
because they are class-based views with a `dispatch` method.

```python
from rest_framework import generics
from django_ip_access import IPAccessMixin

from .serializers import ItemSerializer
from .models import Item


class SecureItemListView(IPAccessMixin, generics.ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    # Optional: customise matching
    # ip_access_route_config = {
    #     "pattern": "/api/items/",
    #     "type": "exact",
    # }
```

You can also use the decorator on DRF `APIView` methods (or plain DRF FBVs):

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from django_ip_access.decorators import ip_access_required


class SecureStatusView(APIView):
    @ip_access_required()
    def get(self, request, *args, **kwargs):
        return Response({"status": "ok"})
```

### Django REST framework: viewsets

For DRF viewsets, you can mix in `IPAccessMixin` as well, since viewsets
inherit from `APIView`:

```python
from rest_framework import viewsets
from django_ip_access import IPAccessMixin

from .serializers import ItemSerializer
from .models import Item


class SecureItemViewSet(IPAccessMixin, viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
```

The deny response automatically adapts:
- For DRF `Request` objects, it returns a DRF `Response` with a JSON payload.
- For regular Django requests, it returns JSON (for XHR/JSON clients) or an
  HTML response for browsers.

## Django Admin

The middleware includes a Django admin interface for managing granted IPs at `/admin/`:

- View all granted IPs
- Add/edit/delete IP addresses and ranges
- Enable/disable IP entries
- Filter and search

## Models

### GrantedIP

- `ip_address`: IP address or CIDR range (e.g., `192.168.1.1` or `192.168.1.0/24`)
- `description`: Optional description
- `is_active`: Enable/disable the IP entry
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Requirements

- Python 3.8+
- Django 3.2+

### Optional Dependencies

- `netifaces`: For better network interface detection (install with `pip install django-ip-access-middleware[dev]`)

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on GitHub.

