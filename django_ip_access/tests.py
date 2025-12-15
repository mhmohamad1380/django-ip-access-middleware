from django.http import HttpResponse
from django.test import RequestFactory, TestCase, override_settings
from django.views import View

from .mixins import IPAccessMixin
from .decorators import ip_access_required
from .models import GrantedIP


class IPAccessMixinTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(
        IP_ACCESS_MIDDLEWARE_CONFIG={
            "DENY_MESSAGE": "Access denied",
            "DENY_STATUS_CODE": 403,
            "routes": [],
            "kubernetes_network_range": "",
            "pod_ip": "",
        },
        ALLOWED_HOSTNAMES_ENV="",
    )
    def test_mixin_denies_when_ip_not_granted(self):
        """
        If the client IP is not in GrantedIP, the mixin should deny access.
        """
        request = self.factory.get("/secure/")
        # Simulate a remote IP that is not in the database.
        request.META["REMOTE_ADDR"] = "203.0.113.10"

        class SecureView(IPAccessMixin, View):
            def get(self, request, *args, **kwargs):
                return HttpResponse("ok")

        response = SecureView.as_view()(request)
        self.assertEqual(response.status_code, 403)
        self.assertIn(b"Access denied", response.content)

    @override_settings(
        IP_ACCESS_MIDDLEWARE_CONFIG={
            "DENY_MESSAGE": "Access denied",
            "DENY_STATUS_CODE": 403,
            "routes": [],
            "kubernetes_network_range": "",
            "pod_ip": "",
        },
        ALLOWED_HOSTNAMES_ENV="",
    )
    def test_mixin_allows_when_ip_granted(self):
        """
        If the client IP is in GrantedIP, the mixin should allow access.
        """
        GrantedIP.objects.create(ip_address="203.0.113.10", is_active=True)

        request = self.factory.get("/secure/")
        request.META["REMOTE_ADDR"] = "203.0.113.10"

        class SecureView(IPAccessMixin, View):
            def get(self, request, *args, **kwargs):
                return HttpResponse("ok")

        response = SecureView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"ok")


class IPAccessDecoratorTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(
        IP_ACCESS_MIDDLEWARE_CONFIG={
            "DENY_MESSAGE": "Denied",
            "DENY_STATUS_CODE": 401,
            "routes": [],
            "kubernetes_network_range": "",
            "pod_ip": "",
        },
        ALLOWED_HOSTNAMES_ENV="",
    )
    def test_decorator_denies_when_ip_not_granted(self):
        """
        Decorated function-based view should be denied if IP is not granted.
        """

        @ip_access_required()
        def view(request):
            return HttpResponse("ok")

        request = self.factory.get("/secure-fbv/")
        request.META["REMOTE_ADDR"] = "198.51.100.5"

        response = view(request)
        self.assertEqual(response.status_code, 401)
        self.assertIn(b"Denied", response.content)

    @override_settings(
        IP_ACCESS_MIDDLEWARE_CONFIG={
            "DENY_MESSAGE": "Denied",
            "DENY_STATUS_CODE": 401,
            "routes": [],
            "kubernetes_network_range": "",
            "pod_ip": "",
        },
        ALLOWED_HOSTNAMES_ENV="",
    )
    def test_decorator_allows_when_ip_granted(self):
        """
        Decorated function-based view should be allowed when IP is granted.
        """
        GrantedIP.objects.create(ip_address="198.51.100.5", is_active=True)

        @ip_access_required()
        def view(request):
            return HttpResponse("ok")

        request = self.factory.get("/secure-fbv/")
        request.META["REMOTE_ADDR"] = "198.51.100.5"

        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"ok")


try:
    # Only define DRF-specific tests if DRF is installed.
    from rest_framework.test import APIRequestFactory  # type: ignore
    from rest_framework.views import APIView  # type: ignore
    from rest_framework.response import Response  # type: ignore

    class DRFIntegrationTests(TestCase):
        def setUp(self):
            self.factory = APIRequestFactory()

        @override_settings(
            IP_ACCESS_MIDDLEWARE_CONFIG={
                "DENY_MESSAGE": "Access denied",
                "DENY_STATUS_CODE": 403,
                "routes": [],
                "kubernetes_network_range": "",
                "pod_ip": "",
            },
            ALLOWED_HOSTNAMES_ENV="",
        )
        def test_mixin_with_drf_apiview(self):
            """
            IPAccessMixin should work with DRF APIView subclasses.
            """

            class SecureAPIView(IPAccessMixin, APIView):
                def get(self, request, *args, **kwargs):
                    return Response({"detail": "ok"})

            request = self.factory.get("/drf-secure/")
            request.META["REMOTE_ADDR"] = "203.0.113.20"

            # No GrantedIP entry: should be denied.
            response = SecureAPIView.as_view()(request)
            self.assertEqual(response.status_code, 403)

            # Add GrantedIP and try again.
            GrantedIP.objects.create(ip_address="203.0.113.20", is_active=True)
            request = self.factory.get("/drf-secure/")
            request.META["REMOTE_ADDR"] = "203.0.113.20"
            response = SecureAPIView.as_view()(request)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data, {"detail": "ok"})

        @override_settings(
            IP_ACCESS_MIDDLEWARE_CONFIG={
                "DENY_MESSAGE": "Denied",
                "DENY_STATUS_CODE": 403,
                "routes": [],
                "kubernetes_network_range": "",
                "pod_ip": "",
            },
            ALLOWED_HOSTNAMES_ENV="",
        )
        def test_decorator_with_drf_apiview_method(self):
            """
            ip_access_required should work on DRF APIView methods.
            """

            class SecureStatusView(APIView):
                @ip_access_required()
                def get(self, request, *args, **kwargs):
                    return Response({"status": "ok"})

            request = self.factory.get("/drf-status/")
            request.META["REMOTE_ADDR"] = "198.51.100.50"

            # No GrantedIP: denied.
            response = SecureStatusView.as_view()(request)
            self.assertEqual(response.status_code, 403)

            GrantedIP.objects.create(ip_address="198.51.100.50", is_active=True)
            request = self.factory.get("/drf-status/")
            request.META["REMOTE_ADDR"] = "198.51.100.50"
            response = SecureStatusView.as_view()(request)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data, {"status": "ok"})

except ImportError:  # pragma: no cover
    # DRF is not installed; skip DRF integration tests.
    pass


