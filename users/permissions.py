from rest_framework.permissions import BasePermission


class IsAdminHost(BasePermission):
    def has_permission(self, request, view):
        return request.is_admin_host


class IsNotAdminHost(BasePermission):
    def has_permission(self, request, view):
        return not request.is_admin_host


class EmailVerified(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.email_verified


class MobileVerified(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.mobile_verified


class IsAdminUserOrEmailVerified(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_staff
            or request.user.is_superuser
            or (request.user.is_authenticated and request.user.email_verified)
        )
