"""
Django IP Access Control Middleware

A Django middleware for IP and hostname-based access control with support for:
- IP addresses and CIDR ranges from database
- Hostname matching from environment variables
- Automatic same-network detection for Kubernetes
- Route-based access control with regex, exact, startswith, endswith patterns
"""

__version__ = '1.0.0'
__author__ = 'Your Name'
__email__ = 'your.email@example.com'

default_app_config = 'django_ip_access.apps.DjangoIpAccessConfig'

