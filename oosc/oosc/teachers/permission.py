from rest_framework.permissions import BasePermission

class IsHeadteacherOrAdmin(BasePermission):
    message="You must be the school's headteacher of Unicef personnel"
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        else:
            return request.user.id == obj.school.headteacher