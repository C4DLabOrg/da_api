from rest_framework.permissions import BasePermission
from oosc.partner.models import Partner
from django.contrib.auth.models import User, Group

SAFE=["OPTIONS","POST","HEAD"]
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        is_in_unicef = Group.objects.get(name="unicef").user_set.filter(id=request.user.id).exists()
        if(is_in_unicef or request.user and request.user.is_authenticated() and request.user.is_superuser):
            return True
        return False
