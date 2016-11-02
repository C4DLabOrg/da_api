from django.shortcuts import render
from rest_framework import generics
# Create your views here.
from oosc.classes.models import Classes
from oosc.classes.serializers import ClassesSerializer
class ListCreateClass(generics.ListCreateAPIView):
    queryset = Classes.objects.all()
    serializer_class = ClassesSerializer
