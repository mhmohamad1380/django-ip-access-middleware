"""
Admin configuration for IP Access Control Middleware models
"""
from django.contrib import admin
from .models import GrantedIP


@admin.register(GrantedIP)
class GrantedIPAdmin(admin.ModelAdmin):
    """
    Admin interface for managing granted IP addresses.
    """
    list_display = ('ip_address', 'is_active', 'description', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('ip_address', 'description')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('IP Configuration', {
            'fields': ('ip_address', 'is_active')
        }),
        ('Additional Information', {
            'fields': ('description',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make created_at and updated_at readonly."""
        return self.readonly_fields

