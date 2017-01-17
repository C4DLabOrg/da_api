from django.shortcuts import render

# Create your views here.
from oosc.absence.models import Absence
from oosc.absence.serializers import AbsenceSerializer
from rest_framework import generics

class GetEditAbsence(generics.RetrieveUpdateAPIView):
    queryset = Absence.objects.all()
    serializer_class = AbsenceSerializer

