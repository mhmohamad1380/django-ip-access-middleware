"""
App configuration for Django IP Access Control Middleware
"""
from django.apps import AppConfig


class DjangoIpAccessConfig(AppConfig):
    """Configuration for django_ip_access app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_ip_access'
    verbose_name = 'Django IP Access Control'

