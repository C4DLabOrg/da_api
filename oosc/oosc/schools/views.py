from django.shortcuts import render
from oosc.schools.models import Schools
from rest_framework import generics
from oosc.schools.serializers import SchoolsSerializer
# Create your views here.

class ListCreateSchool(generics.ListCreateAPIView):
    queryset=Schools.objects.all();
    serializer_class=SchoolsSerializer