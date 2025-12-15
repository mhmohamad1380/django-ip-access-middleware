"""
Django IP Access Control Middleware

A Django middleware for IP and hostname-based access control with support for:
- IP addresses and CIDR ranges from database
- Hostname matching from environment variables
- Automatic same-network detection for Kubernetes
- Route-based access control with regex, exact, startswith, endswith patterns
"""

__version__ = '1.0.4'
__author__ = 'Mohammad Mohammad Hosseini'
__email__ = 'dev.mohammadhosseiny@gmail.com'

default_app_config = 'django_ip_access.apps.DjangoIpAccessConfig'

