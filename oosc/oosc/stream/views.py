import django_filters
from django.shortcuts import  get_object_or_404
from django.http import Http404
from rest_framework import generics
# Create your views here.
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from oosc.stream.models import Stream
from oosc.stream.serializers import StreamSerializer, GetStreamSerializer
from django_filters.rest_framework import FilterSet,DjangoFilterBackend

class StreamFilter(FilterSet):
    partner_admin=django_filters.NumberFilter(name="active" ,label="Partner Admin" ,method="filter_partner_admin")
    class Meta:
        model=Stream
        fields=('school','class_name')

    def filter_partner_admin(self, queryset, name, value):
        return queryset.filter(school__partners__partner_admins__id=value)

class ListCreateClass(generics.ListCreateAPIView):
    queryset = Stream.objects.all()
    serializer_class = StreamSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class=StreamFilter


    def get_queryset(self):
        return self.queryset.order_by("school","_class","class_name")



    def get_serializer_class(self):
        print(self.request.method)
        if self.request.method == "GET":
            return GetStreamSerializer
        return StreamSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ##Confirm it does not exist
        sch=serializer.validated_data.get("school")
        cl=serializer.validated_data.get("class_name")
        _cl=serializer.validated_data.get("class_name")
        # print (cl.upper())
        d=list(Stream.objects.filter(class_name=cl.upper(),school_id=sch))
        if len(d) > 0:
            ser=StreamSerializer(d[0])
            return Response(ser.data, status=status.HTTP_200_OK)
        else:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


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

    def get_serializer_class(self):
        if self.request.method == "GET":
            return GetStreamSerializer
        return StreamSerializer

    def get_delete_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        id=filter_kwargs["pk"]
        if not Stream.objects.filter(id=filter_kwargs["pk"]).exists():
            raise StreamNotFound

        objs=list(Stream.objects.filter(id=filter_kwargs["pk"]).filter(students=None))
        # print(objs,id)
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



