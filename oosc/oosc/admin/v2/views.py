from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from oosc.admin.v2.serializers import ResetPasswordSerializer, SchoolEmiscodesSerializer
from oosc.mylib.common import MyCustomException
from oosc.stream.models import Stream


class RestPassword(generics.UpdateAPIView):
    serializer_class =ResetPasswordSerializer
    queryset = User.objects.all()
    # permission_classes = []

    def update(self, serializer):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.get_object()
        if instance.is_superuser:
            raise MyCustomException("Admin account.",403)
        passwd=self.request.data.get("password","admin")
        instance.set_password(passwd)
        instance.save()
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        return Response({"detail":"Password successfully changed."})

    def get_object(self):
        username=self.request.data["username"]
        filter_kwargs={"username":username}
        obj = get_object_or_404(self.queryset, **filter_kwargs)
        # May raise a permission denied
        self.check_object_permissions(self.request, obj)
        return obj


class DeleteStreams(generics.DestroyAPIView):

    serializer_class =SchoolEmiscodesSerializer
    queryset = Stream.objects.all()

    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        emis_codes=serializer.validated_data.get("emis_codes")
        dele=Stream.objects.filter(school__emis_code__in=emis_codes).delete()
        return Response({"total":dele[0],"objects":dele[1]},status=status.HTTP_202_ACCEPTED)
