from django.contrib.auth.models import User
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from oosc.admin.v2.serializers import ResetPasswordSerializer, SchoolEmiscodesSerializer, \
    DeleteStreamStudentsSerializer, SchoolsSerializerV2
from oosc.mylib.common import MyCustomException
from oosc.schools.models import Schools
from oosc.schools.views import SchoolsFilter
from oosc.stream.models import Stream
from oosc.teachers.models import Teachers
from oosc.teachers.serializers import TeacherSerializer


class RestPassword(generics.UpdateAPIView):
    serializer_class = ResetPasswordSerializer
    queryset = User.objects.all()

    # permisfsion_classes = []

    def update(self, serializer):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.get_object()
        if instance.is_superuser:
            raise MyCustomException("Admin account.", 403)
        passwd = serializer.validated_data.get("password")
        instance.set_password(passwd)
        instance.save()
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        return Response({"detail": "Password successfully changed."})

    def get_object(self):
        username = self.request.data["username"]
        filter_kwargs = {"username": username}
        obj = get_object_or_404(self.queryset, **filter_kwargs)
        # May raise a permission denied
        self.check_object_permissions(self.request, obj)
        return obj


class RetrieveDeleteStream(generics.RetrieveUpdateDestroyAPIView):
    queryset = Teachers.objects.all()
    serializer_class = TeacherSerializer

    def perform_update(self, serializer):
        serializer.save()
        try:
            user = serializer.validated_data.get("user")
            user.set_password("admin")
            user.save()
        except:
            raise MyCustomException("Failed to update password", 404)

    def get_object(self):
        username = self.kwargs["pk"]
        teachers = list(Teachers.objects.filter(user__username=username))
        if len(teachers) < 1:
            if User.objects.filter(username=username).exists():
                raise MyCustomException("User has no associated teacher account.")
            else:
                raise MyCustomException("The teacher does not exist.")
        tech = teachers[0]
        if tech.non_delete:
            tech.headteacher = True
        return tech


class DeleteStreams(generics.DestroyAPIView):
    serializer_class = SchoolEmiscodesSerializer
    queryset = Stream.objects.all()

    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        emis_codes = serializer.validated_data.get("emis_codes")
        dele = Stream.objects.filter(school__emis_code__in=emis_codes).delete()
        return Response({"total": dele[0], "objects": dele[1]}, status=status.HTTP_202_ACCEPTED)


class DeleteStudentsByStreams(generics.DestroyAPIView):
    serializer_class = DeleteStreamStudentsSerializer
    queryset = Stream.objects.all()

    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        streams = serializer.validated_data.get("streams")
        dele = Stream.objects.filter(id__in=streams).delete()
        print(dele)
        return Response({"total": dele[0], "objects": dele[1]}, status=status.HTTP_202_ACCEPTED)


class ListDuplicatePartnerSchools(generics.ListCreateAPIView):
    serializer_class = SchoolsSerializerV2
    queryset = Schools.objects.all()
    # pagination_class = ""
    filter_backends = (DjangoFilterBackend,)
    filter_class = SchoolsFilter

    def get_queryset(self):
        return self.queryset.filter(active=True).annotate(partners_count=Count("partners")).filter(
            partners_count__gte=2)
