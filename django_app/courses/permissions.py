from rest_framework import permissions
from subscriptions.utils import has_active_subscription

class HasActiveSubscription(permissions.BasePermission):
    message = "You must have an active subscription to access this content."

    def has_permission(self, request, view):
        return request.user.is_authenticated and has_active_subscription(request.user)
