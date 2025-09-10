from django.conf import settings
from rest_framework import permissions

class IsServiceToken(permissions.BasePermission):
    def has_permission(self, request, view):
        expected_token = getattr(settings, "SERVICE_API_TOKEN", None)
        provided = request.headers.get("Authorization", "").replace("Token ", "")
        return expected_token and provided == expected_token
