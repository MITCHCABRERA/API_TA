from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """Allows access only to admin users."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsOwnerOrAdmin(permissions.BasePermission):
    """Allows access to resource owners or admins."""
    
    def has_object_permission(self, request, view, obj):
        return request.user == obj.author or request.user.role == 'admin'


class CanViewPost(permissions.BasePermission):
    """Enforces post privacy settings."""
    
    def has_object_permission(self, request, view, obj):
        if obj.privacy == 'public':
            return True
        return request.user == obj.author
