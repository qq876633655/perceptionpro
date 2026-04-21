from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if user.is_superuser:
            return True

        return user.groups.filter(name='dev').exists()
