from rest_framework.permissions import BasePermission


class HasAccountableRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.has_perm("tickets.accountable")
