from django.shortcuts import render
from oosc.attendance.models import Attendance
from rest_framework import generics
from oosc.attendance.serializers import AttendanceSerializer
# Create your views here.

class ListCreateAttendance(generics.ListCreateAPIView):
    queryset=Attendance.objects.all();
    serializer_class=AttendanceSerializer
