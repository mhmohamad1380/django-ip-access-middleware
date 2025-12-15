## Release notes

This page mirrors the project changelog. The canonical source is
`CHANGELOG.md` at the root of the repository.

---

## [1.1.0] - UNDER DEVELOPMENT

### Summary

Adds opt-in IP/hostname access control for individual views via mixins and a
decorator, with first-class support for Django REST framework, while remaining
backwards compatible.

### Added

- `IPAccessMixin` in `django_ip_access.mixins` for protecting specific
  class-based views:
  - Works with standard Django CBVs, DRF generic views, and DRF viewsets.
  - Supports optional `ip_access_route_config` on the view to customize route
    matching (e.g. `startswith`, `regex`).
- `ip_access_required` decorator in `django_ip_access.decorators` for:
  - Django function-based views.
  - DRF `APIView` methods (e.g. `get`, `post`).
- New documentation examples demonstrating:
  - Usage with Django CBVs.
  - Usage with DRF generics, APIViews, and viewsets.
- Test coverage for:
  - `IPAccessMixin` with allowed/denied IPs.
  - `ip_access_required` on Django FBVs and DRF APIViews.

### Changed

- `django_ip_access.__init__` now re-exports:
  - `IPAccessMixin` from `django_ip_access.mixins`.
  - `ip_access_required` from `django_ip_access.decorators`.
- Internal organization: decorators moved into a dedicated `decorators.py`
  module (no behavioral change).

### Fixed

- None.

### Notes

- This is a **backwards-compatible** minor release.
- Existing imports like `from django_ip_access import ip_access_required`
  continue to work.
- Recommended usage for new code:
  - `from django_ip_access.mixins import IPAccessMixin`
  - `from django_ip_access.decorators import ip_access_required`

---

## [1.0.4] - 2025-12-14

Initial public release of `django-ip-access-middleware` with:

- Middleware-based IP and hostname access control.
- Database-driven `GrantedIP` model.
- Kubernetes same-network detection.
- Route configuration via `IP_ACCESS_MIDDLEWARE_CONFIG`.


