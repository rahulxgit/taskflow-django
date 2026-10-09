from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Custom permission to only allow owners of an object to edit/delete it."""

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner/creator
        owner = getattr(obj, "owner", getattr(obj, "creator", getattr(obj, "author", None)))
        return owner == request.user
