## API Reference

This section gives a high-level overview of the main public interfaces. For
full details, refer to the docstrings in the code.

### Middleware

- **`django_ip_access.middleware.IPAccessMiddleware`**
  - Main middleware that performs IP and hostname checks for each request.

### Models

- **`django_ip_access.models.GrantedIP`**
  - `ip_address`: IP address or CIDR range (e.g. `192.168.1.1` or `192.168.1.0/24`).
  - `description`: Optional description.
  - `is_active`: Whether this entry is currently enforced.
  - `created_at`, `updated_at`: Timestamps.

### Mixins

- **`django_ip_access.mixins.IPAccessMixin`**
  - Mixin for Django class-based views and DRF views/viewsets.
  - Optional attribute `ip_access_route_config` to customise route matching:
    - `pattern`: string.
    - `type`: `"regex" | "exact" | "startswith" | "endswith"`.

### Decorators

- **`django_ip_access.decorators.ip_access_required(route_config=None)`**
  - Decorator for function-based views (including DRF FBVs).
  - `route_config` has the same shape as `ip_access_route_config` on the mixin.


