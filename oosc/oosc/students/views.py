from django.shortcuts import render
from oosc.students.models import Students
from rest_framework import generics
from oosc.students.serializers import StudentsSerializer
# Create your views here.

class ListCreateStudent(generics.ListCreateAPIView):
    queryset=Students.objects.all()
    serializer_class=StudentsSerializer