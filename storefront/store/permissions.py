from rest_framework import permissions


class IsAdminorReadOnly(permissions.BasePermission):
    """ a custom permission to access list of customers"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)