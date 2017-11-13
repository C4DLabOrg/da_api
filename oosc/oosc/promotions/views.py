from django.shortcuts import render

# Create your views here.

from rest_framework import generics

from oosc.promotions.models import PromoteSchool
from oosc.promotions.serializers import PromoteSchoolSerializer


class PromoteStudents(generics.ListCreateAPIView):
    queryset = PromoteSchool.objects.all()
    serializer_class =PromoteSchoolSerializer