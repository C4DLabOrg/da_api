from rest_framework.permissions import BasePermission
from oosc.partner.models import Partner
from django.contrib.auth.models import User, Group

SAFE=["OPTIONS","GET","HEAD"]
class IsAdmin(BasePermission):
    message="Only unicef admins are allowed"
    def has_permission(self, request, view):
        if  request.method in SAFE :
            return True
        group,created=Group.objects.get_or_create(name="unicef")
        is_in_unicef = group.user_set.filter(id=request.user.id).exists()
        if( ( is_in_unicef or request.user.is_superuser ) and request.user.is_authenticated() and request.user):
            return True
        return False
