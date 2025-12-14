"""
Database models for IP Access Control Middleware
"""
from django.db import models
from django.core.validators import validate_ipv46_address, RegexValidator


class GrantedIP(models.Model):
    """
    Model to store granted IP addresses and IP ranges.
    Routes are configured in environment variables/settings, not in this model.
    """
    ip_address = models.CharField(
        max_length=50,
        help_text="IP address or CIDR range (e.g., '192.168.1.1' or '192.168.1.0/24')",
        validators=[
            RegexValidator(
                regex=r'^[\d\./:]+$',
                message='Enter a valid IP address or CIDR range'
            )
        ]
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Optional description for this IP entry"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this IP entry is active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'granted_ips'
        verbose_name = 'Granted IP'
        verbose_name_plural = 'Granted IPs'
        indexes = [
            models.Index(fields=['ip_address', 'is_active']),
        ]

    def __str__(self):
        return f"{self.ip_address} ({'Active' if self.is_active else 'Inactive'})"

