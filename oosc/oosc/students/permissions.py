from rest_framework.permissions import BasePermission
from django.contrib.auth.models import Group
class IsTeacherOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        else:
            request.user.groups.filter(name="teacher").exists()

class IsTeacherOrPartner(BasePermission):
    message = "You must be a teacher or an authorized partner"
    def has_permission(self, request, view):
        is_a_teacher = Group.objects.get(name="teachers").user_set.filter(id=request.user.id).exists()
        is_a_partner = Group.objects.get(name="partners").user_set.filter(id=request.user.id).exists()

        if is_a_partner or is_a_teacher and request.user and request.user.is_authenticated():
            return True
        return False