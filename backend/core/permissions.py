from rest_framework.permissions import SAFE_METHODS, BasePermission


class AuthorAdminOrReadOnly(BasePermission):
    """
    Access to create only for authenticated users,
    to patch, delete for author, admin,
    or read only.
    """

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user.is_authenticated
                or request.user.is_superuser
                )

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS or request.user.is_superuser:
            return True
        if hasattr(obj, 'author'):
            return obj.author == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
