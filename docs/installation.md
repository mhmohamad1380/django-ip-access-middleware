## Installation & Setup

### Install the package

Install the package from PyPI:

```bash
pip install django-ip-access-middleware
```

Or install from a local clone in editable mode:

```bash
pip install -e .
```

### Add to `INSTALLED_APPS`

In your Django `settings.py`:

```python
INSTALLED_APPS = [
    # ... other apps
    "django_ip_access",
]
```

### Add the middleware

Add the IP access middleware to your `MIDDLEWARE` list:

```python
MIDDLEWARE = [
    # ... other middleware
    "django_ip_access.middleware.IPAccessMiddleware",
    # ... other middleware
]
```

### Run migrations

Create and apply migrations for the `GrantedIP` model:

```bash
python manage.py makemigrations django_ip_access
python manage.py migrate django_ip_access
```


