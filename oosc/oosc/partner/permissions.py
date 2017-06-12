from rest_framework.permissions import BasePermission
from oosc.partner.models import Partner
from django.contrib.auth.models import User

SAFE=["OPTIONS","POST","HEAD"]
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if(request.method in SAFE or request.user and request.user.is_authenticated() and request.user.is_superuser):
            return True
        return False
