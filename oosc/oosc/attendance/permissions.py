from rest_framework.permissions import BasePermission
from django.contrib.auth.models import Group

class IsTeacherOfTheSchool(BasePermission):

    def has_permission(self, request, view):
        is_in_group=Group.objects.get(name="teachers").user_set.filter(id=request.user.id).exists()
        if(request.user and request.user.is_authenticated() and  request.user and is_in_group):
            return True
        return False