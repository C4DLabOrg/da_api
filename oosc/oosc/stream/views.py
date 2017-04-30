from django.shortcuts import render
from rest_framework import generics
# Create your views here.
from oosc.stream.models import Stream
from oosc.stream.serializers import StreamSerializer
class ListCreateClass(generics.ListCreateAPIView):
    queryset = Stream.objects.all()
    serializer_class = StreamSerializer
