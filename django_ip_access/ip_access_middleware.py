"""
IP and Hostname Access Control Middleware

This middleware supports:
- IP addresses (single) from database
- IP ranges (CIDR notation) from database
- Hostnames from environment variables
- Same network detection for Kubernetes (highest priority)
- Route matching with regex, exact match, startswith, endswith

Priority order:
1. Same network detection (Kubernetes) - if same network, allow and skip IP check
2. Hostname check (from environment variables)
3. IP check (from database)
"""
import ipaddress
import os
import re
import socket
from typing import List, Dict, Union, Optional
from django.http import HttpResponse, HttpRequest
from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import ImproperlyConfigured

# Optional import for better network interface detection
try:
    import netifaces
    NETIFACES_AVAILABLE = True
except ImportError:
    NETIFACES_AVAILABLE = False


class IPAccessMiddleware(MiddlewareMixin):
    """
    Middleware for IP and hostname-based access control.
    
    Configuration:
    1. Routes are configured in settings.py IP_ACCESS_MIDDLEWARE_CONFIG['routes']
    2. Granted IPs are stored in the database (GrantedIP model)
    3. Allowed hostnames are read from ALLOWED_HOSTNAMES environment variable (comma-separated)
    4. Kubernetes same-network detection is automatic, but can be configured via:
       - POD_IP environment variable (optional, for explicit pod IP)
       - KUBERNETES_NETWORK_RANGE environment variable (optional, for explicit network range)
    
    Same network detection automatically works if:
    - Both client and server IPs are private IPs and on the same subnet
    - Client IP is in the configured KUBERNETES_NETWORK_RANGE (if set)
    - Client and server POD_IPs are on the same network (if POD_IP is set)
    
    Example environment variables:
    - ALLOWED_HOSTNAMES="*.example.com,api.example.com,*.subdomain.com"
    - POD_IP="10.244.1.5" (optional, Kubernetes pod IP)
    - KUBERNETES_NETWORK_RANGE="10.244.0.0/16" (optional, Kubernetes pod network range)
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.config = self._load_config()
        self.allowed_hostnames = self._load_hostnames_from_env()
        self.kubernetes_network_range = self.config.get('kubernetes_network_range')
        self.pod_ip = self.config.get('pod_ip')
        super().__init__(get_response)
    
    def _load_config(self) -> Dict:
        """Load configuration from Django settings."""
        from django.conf import settings
        return getattr(settings, 'IP_ACCESS_MIDDLEWARE_CONFIG', {
            'routes': [],
            'kubernetes_network_range': '',
            'pod_ip': '',
        })
    
    def _load_hostnames_from_env(self) -> List[str]:
        """Load allowed hostnames from environment variable."""
        from django.conf import settings
        hostnames_str = getattr(settings, 'ALLOWED_HOSTNAMES_ENV', '')
        if not hostnames_str:
            return []
        # Split by comma and strip whitespace
        return [h.strip() for h in hostnames_str.split(',') if h.strip()]
    
    def _get_granted_ips_from_db(self) -> List[str]:
        """
        Fetch all active granted IP addresses from the database.
        
        Returns:
            List of IP addresses/ranges from database.
        """
        try:
            from .models import GrantedIP
            return list(GrantedIP.objects.filter(is_active=True).values_list('ip_address', flat=True))
        except Exception as e:
            # If database is not ready or model doesn't exist yet, return empty list
            # This prevents issues during migrations
            return []
    
    def _get_client_ip(self, request: HttpRequest) -> Optional[str]:
        """
        Get the client IP address from request.
        Checks X-Forwarded-For, X-Real-IP, and REMOTE_ADDR.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # X-Forwarded-For can contain multiple IPs, take the first one
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR')
        return ip
    
    def _get_client_hostname(self, request: HttpRequest) -> Optional[str]:
        """
        Get the client hostname from request.
        Priority: Host header, then resolve IP to hostname.
        """
        # First, try to get from Host header
        hostname = request.META.get('HTTP_HOST', '').split(':')[0]
        if hostname:
            return hostname
        
        # Try to resolve IP to hostname
        ip = self._get_client_ip(request)
        if ip:
            try:
                hostname = socket.gethostbyaddr(ip)[0]
                return hostname
            except (socket.herror, socket.gaierror, ValueError):
                pass
        
        return None
    
    def _is_ip_in_range(self, ip: str, ip_range: str) -> bool:
        """
        Check if an IP address is within a range (CIDR notation).
        Also supports single IP addresses.
        """
        try:
            ip_obj = ipaddress.ip_address(ip)
            # Try CIDR notation first
            if '/' in ip_range:
                network = ipaddress.ip_network(ip_range, strict=False)
                return ip_obj in network
            else:
                # Single IP address
                return str(ip_obj) == ip_range
        except (ValueError, ipaddress.AddressValueError):
            return False
    
    def _is_hostname_match(self, hostname: str, pattern: str) -> bool:
        """
        Check if hostname matches pattern (supports wildcards like *.example.com).
        """
        if not hostname or not pattern:
            return False
        
        # Exact match
        if hostname == pattern:
            return True
        
        # Wildcard match (e.g., *.example.com)
        if pattern.startswith('*.'):
            domain = pattern[2:]  # Remove '*.'
            return hostname.endswith('.' + domain) or hostname == domain
        
        # Regex pattern
        try:
            return bool(re.match(pattern, hostname))
        except re.error:
            return False
    
    def _get_server_ip(self) -> Optional[str]:
        """
        Get the server's IP address automatically.
        Tries multiple methods to detect the server IP.
        """
        # Method 1: Try POD_IP environment variable (Kubernetes)
        pod_ip = os.getenv('POD_IP') or self.pod_ip
        if pod_ip:
            return pod_ip
        
        # Method 2: Try to get IP from network interfaces
        try:
            # Try to connect to a remote address to determine default route interface
            # This is a common trick to get the local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                # Connect to a non-routable address (doesn't actually send data)
                s.connect(('10.255.255.255', 1))
                server_ip = s.getsockname()[0]
                s.close()
                return server_ip
            except Exception:
                s.close()
        except Exception:
            pass
        
        # Method 3: Try netifaces if available (for more accurate detection)
        if NETIFACES_AVAILABLE:
            try:
                # Get default gateway interface
                gateways = netifaces.gateways()
                default_interface = gateways['default'].get(netifaces.AF_INET, [None])[1]
                if default_interface:
                    addrs = netifaces.ifaddresses(default_interface)
                    if netifaces.AF_INET in addrs:
                        server_ip = addrs[netifaces.AF_INET][0].get('addr')
                        if server_ip and not server_ip.startswith('127.'):
                            return server_ip
            except Exception:
                pass
        
        return None
    
    def _is_same_kubernetes_network(self, client_ip: str) -> bool:
        """
        Automatically detect if client IP is on the same Kubernetes/network as the server.
        This allows all pods/services in the same cluster to communicate without explicit configuration.
        
        Detection methods (in order):
        1. If KUBERNETES_NETWORK_RANGE is set, check if client IP is in that range
        2. If POD_IP is set, check if client and server are on the same network
        3. Auto-detect server IP and check if client and server are on the same private network
        """
        if not client_ip:
            return False
        
        try:
            client_ip_obj = ipaddress.ip_address(client_ip)
            
            # Skip loopback addresses
            if client_ip_obj.is_loopback:
                return True
            
            # Method 1: Check if client IP is in explicitly configured Kubernetes network range
            if self.kubernetes_network_range:
                try:
                    k8s_network = ipaddress.ip_network(self.kubernetes_network_range, strict=False)
                    if client_ip_obj in k8s_network:
                        return True
                except (ValueError, ipaddress.AddressValueError):
                    pass
            
            # Method 2: Get server IP and check if they're on the same network
            server_ip = self._get_server_ip()
            if server_ip:
                try:
                    server_ip_obj = ipaddress.ip_address(server_ip)
                    
                    # Skip if server IP is loopback (not useful for K8s detection)
                    if server_ip_obj.is_loopback:
                        return False
                    
                    # Check if both are private IPs (common in Kubernetes)
                    if client_ip_obj.is_private and server_ip_obj.is_private:
                        # Check multiple subnet sizes for flexibility
                        for prefix_len in [16, 24]:
                            client_network = ipaddress.ip_network(f"{client_ip}/{prefix_len}", strict=False)
                            server_network = ipaddress.ip_network(f"{server_ip}/{prefix_len}", strict=False)
                            if client_network == server_network:
                                return True
                    
                    # Also check exact network match for common K8s ranges
                    # Kubernetes often uses 10.x.x.x, 172.16-31.x.x, or 192.168.x.x
                    if (client_ip_obj.is_private and server_ip_obj.is_private and
                        client_ip_obj.version == server_ip_obj.version):
                        # Check if they're in the same /16 network (common for pod networks)
                        client_network_16 = ipaddress.ip_network(f"{client_ip}/16", strict=False)
                        server_network_16 = ipaddress.ip_network(f"{server_ip}/16", strict=False)
                        if client_network_16 == server_network_16:
                            return True
                except (ValueError, ipaddress.AddressValueError):
                    pass
            
            return False
        except (ValueError, ipaddress.AddressValueError):
            return False
    
    def _match_route(self, request_path: str, route_config: Dict) -> bool:
        """
        Check if the request path matches the route pattern.
        Supports: regex, exact, startswith, endswith
        """
        pattern = route_config.get('pattern', '')
        route_type = route_config.get('type', 'exact').lower()
        
        if route_type == 'regex':
            try:
                return bool(re.match(pattern, request_path))
            except re.error:
                return False
        elif route_type == 'exact':
            return request_path == pattern
        elif route_type == 'startswith':
            return request_path.startswith(pattern)
        elif route_type == 'endswith':
            return request_path.endswith(pattern)
        else:
            # Default to exact match
            return request_path == pattern
    
    def _is_access_allowed(self, request: HttpRequest, route_config: Dict) -> bool:
        """
        Check if access is allowed based on IP and hostname.
        
        Priority order:
        1. Same Kubernetes network (highest priority) - if same network, allow immediately
        2. Hostname check (from environment variables)
        3. IP check (from database)
        
        If same network is detected, IP checking is skipped.
        """
        client_hostname = self._get_client_hostname(request)
        client_ip = self._get_client_ip(request)
        
        # Priority 1: Check if client is on same Kubernetes network
        # If same network, allow immediately and skip IP checking
        if client_ip and self._is_same_kubernetes_network(client_ip):
            return True
        
        # Priority 2: Check hostname (from environment variables)
        if client_hostname and self.allowed_hostnames:
            for hostname_pattern in self.allowed_hostnames:
                if self._is_hostname_match(client_hostname, hostname_pattern):
                    return True
        
        # Priority 3: Check IP address from database
        granted_ips = self._get_granted_ips_from_db()
        
        if client_ip and granted_ips:
            for ip_pattern in granted_ips:
                if self._is_ip_in_range(client_ip, ip_pattern):
                    return True
        
        return False
    
    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """
        Process the request and check access control.
        Returns None to continue processing, or HttpResponse to block.
        """
        request_path = request.path
        routes = self.config.get('routes', [])
        
        # Check if any route matches
        for route_config in routes:
            if self._match_route(request_path, route_config):
                # Route matches, check access
                if not self._is_access_allowed(request, route_config):
                    # Access denied
                    return HttpResponse(
                        'Access Denied: Your IP address or hostname is not authorized to access this resource.',
                        status=403
                    )
                # Access allowed, continue
                return None
        
        # No route matched, pass through
        return None
