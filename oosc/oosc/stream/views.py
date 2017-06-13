from django.shortcuts import render
from rest_framework import generics
# Create your views here.
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

