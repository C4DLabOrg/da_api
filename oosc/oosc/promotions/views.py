from django.shortcuts import render

# Create your views here.

from rest_framework import generics

from oosc.promotions.models import PromoteSchool
from oosc.promotions.serializers import PromoteSchoolSerializer


class CreateListPromoteSchool(generics.ListCreateAPIView):
    queryset = PromoteSchool.objects.all()
    serializer_class =PromoteSchoolSerializer


    # def perform_create(self, serializer):
    #     school=serializer.validated_data.get("school")
    #     year=serializer.validated_data.get("year")



class RetrievePromoteSschool(generics.RetrieveUpdateAPIView):
    queryset = PromoteSchool.objects.all()
    serializer_class =PromoteSchoolSerializer