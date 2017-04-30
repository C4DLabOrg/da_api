from django.shortcuts import render
from rest_framework import generics
# Create your views here.
from oosc.counties.models import Counties
from oosc.counties.serializers import CountiesSerializer

class ListCreateCounty(generics.ListCreateAPIView):
    queryset = Counties.objects.all()
    serializer_class = CountiesSerializer

    def perform_create(self, serializer):
        #print (serializer.validated_data)
        serializer.save()


