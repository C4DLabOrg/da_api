from django.shortcuts import  get_object_or_404
from django.http import Http404
from rest_framework import generics
# Create your views here.
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from oosc.stream.models import Stream
from oosc.stream.serializers import StreamSerializer
from django_filters.rest_framework import FilterSet,DjangoFilterBackend

class StreamFilter(FilterSet):
    class Meta:
        model=Stream
        fields=('school','class_name')

class ListCreateClass(generics.ListCreateAPIView):
    queryset = Stream.objects.all()
    serializer_class = StreamSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class=StreamFilter

class ClassHasStudents (APIException):
    status_code = 400
    default_detail = 'The class should have no students.'
    default_code = 'service_unavailable'

class StreamNotFound(APIException):
    status_code = 404
    default_detail = 'Stream does not exist.\n Logout and login again.'
    default_code = 'service_unavailable'

class RetrieveUpdateClass(generics.RetrieveUpdateDestroyAPIView):
    queryset = Stream.objects.all()
    serializer_class = StreamSerializer

    def get_delete_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}

        if not Stream.objects.filter(id=filter_kwargs["pk"]).exists():
            raise StreamNotFound
        objs=list(Stream.objects.filter(id=filter_kwargs["pk"]).filter(students=None))
        if len(objs) != 1:
            raise ClassHasStudents
        obj = objs[0]
        # May raise a permission denied
        self.check_object_permissions(self.request, obj)
        return obj

    def destroy(self, request, *args, **kwargs):
        instance = self.get_delete_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)



