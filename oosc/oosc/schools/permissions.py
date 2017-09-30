from rest_framework.permissions import BasePermission
from django.contrib.auth.models import Group

class IsPartner(BasePermission):
    message="You must be a UNICEF authorized partner"
    def has_permission(self, request, view):
        is_partner=Group.objects.get(name="partners").user_set.filter(id=request.user.id).exists()
        if is_partner:
            return True
        return False