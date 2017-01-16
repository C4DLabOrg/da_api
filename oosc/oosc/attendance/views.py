from django.shortcuts import render
from oosc.attendance.models import Attendance
from rest_framework import generics,status
from datetime import datetime
from oosc.students.models import Students
from oosc.attendance.serializers import AttendanceSerializer
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
class ListCreateAttendance(generics.ListAPIView):
    queryset=Attendance.objects.all()
    serializer_class=AttendanceSerializer

class TakeAttendance(APIView):
    def post(self,request,format=None):
        now=str(datetime.now().date()).replace('-','')
        print (request.data)
        try:
            for i in request.data["present"]:
                student=Students()
                student=Students.objects.filter(id=i)[0]
                student.absence=0
                attendance=Attendance()
                attendance.date=datetime.now().date()
                attendance.id=now+str(i)
                attendance.status=1
                attendance._class=student.class_id
                attendance.student=student
                attendance.save()
                print (attendance.id)
            for i in request.data["absent"]:
                student = Students()
                student = Students.objects.filter(id=i)[0]
                student.absence = student.absence + 1
                attendance = Attendance()
                attendance.date = datetime.now().date()
                attendance.id = now + str(i)
                attendance.status = 0
                attendance._class = student.class_id
                attendance.student = student
                attendance.save()
            return Response(data={"message":"Attendance taken"},status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(data={"error":type(e),"error_description":e.message},status=status.HTTP_400_BAD_REQUEST)




