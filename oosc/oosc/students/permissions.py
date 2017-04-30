from rest_framework.permissions import BasePermission

class IsTeacherOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        else:
            request.user.groups.filter(name="teacher").exists()