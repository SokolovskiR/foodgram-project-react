from rest_framework import permissions


class AuthorAdminOrReadOnly(permissions.BasePermission):
    """
    Access to create only for authenticated users,
    to patch, delete for author, admin,
    or read only.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_anonymous:
            return False
        return (
            obj.user == request.user or 
            request.user.is_superuser or 
            obj.author == request.user
        )