## Configuration

### Route types

Each route entry in `IP_ACCESS_MIDDLEWARE_CONFIG["routes"]` has a `pattern` and
`type`:

- **regex**: Match using regular expressions.
- **exact**: Exact path match.
- **startswith**: Match when the request path starts with the pattern.
- **endswith**: Match when the request path ends with the pattern.

### Environment variables

- **`ALLOWED_HOSTNAMES`**: Comma-separated list of allowed hostnames
  (supports wildcards like `*.example.com,api.example.com`).
- **`POD_IP`**: Kubernetes pod IP (optional, for explicit network detection).
- **`KUBERNETES_NETWORK_RANGE`**: Kubernetes network range
  (e.g. `10.244.0.0/16`).

### Same network detection

The middleware can automatically detect when the client IP is on the same
private network as the server:

- Detects private IPs on the same subnet.
- If same-network is detected, access is allowed with highest priority.

### Deny response behavior

By default, when access is denied:

- For Django REST framework requests, a JSON response is returned.
- For regular Django requests, JSON is returned for XHR/JSON clients and an
  HTML response for browsers.

You can override the deny handler by providing
`"DENY_RESPONSE_HANDLER": "path.to.callable"` in
`IP_ACCESS_MIDDLEWARE_CONFIG`. The callable should accept `(request, reason)`
and return a Django `HttpResponse` (or DRF `Response`).


