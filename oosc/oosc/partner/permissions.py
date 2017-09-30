from rest_framework.permissions import BasePermission
from oosc.partner.models import Partner
from django.contrib.auth.models import User, Group

SAFE=["OPTIONS","GET","HEAD"]
class IsAdmin(BasePermission):
    message="Only unicef admins are allowed"
    def has_permission(self, request, view):
        if  request.method in SAFE :
            return True
        is_in_unicef = Group.objects.get(name="unicef").user_set.filter(id=request.user.id).exists()
        if( ( is_in_unicef or request.user.is_superuser ) and request.user.is_authenticated() and request.user):
            return True
        return False
