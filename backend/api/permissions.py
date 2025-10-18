from rest_framework import permissions


class IsProfessionalUser(permissions.BasePermission):
    """
    Custom permission to only allow users marked as professionals.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_pro