from rest_framework.permissions import BasePermission


class IsAdminHost(BasePermission):
    def has_permission(self, request, view):
        return request.is_admin_host
