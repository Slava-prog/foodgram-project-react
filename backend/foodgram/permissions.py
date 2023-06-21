from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение, позволяющее редактировать
    объекты только администратору.
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_authenticated
            and (request.user.is_admin or request.user.is_superuser)
        )

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_admin
            or request.user.is_superuser
        )


class IsAdminAuthororReadOnly(permissions.BasePermission):
    """
    Разрешение, позволяющее редактировать
    объекты только администратору или автору.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_admin
            or obj.author == request.user
            or request.user.is_superuser
        )


class IsAdmin(permissions.BasePermission):
    """
    Доступ только для администратора.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_superuser
        )
