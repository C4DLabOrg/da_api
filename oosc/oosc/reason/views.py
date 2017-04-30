from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from oosc.reason.models import Reason
from oosc.reason.serializers import ReasonSerializer
class ListCreatereason(generics.ListCreateAPIView):
    queryset = Reason.objects.all()
    serializer_class = ReasonSerializer
