from rest_framework.permissions import BasePermission

from users.permissions import EmailVerified
from users.permissions import IsAdminHost
from users.permissions import MobileVerified


class HasAccountableRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.has_perm("tickets.accountable")


class HasAccountableRoleOrEmailAndMobileVerified(BasePermission):
    def has_permission(self, request, view):
        return (
            IsAdminHost().has_permission(request, view)
            and HasAccountableRole().has_permission(request, view)
        ) or (
            EmailVerified().has_permission(request, view)
            and MobileVerified().has_permission(request, view)
        )
