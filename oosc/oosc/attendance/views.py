from django.shortcuts import render
from oosc.attendance.models import Attendance
from rest_framework import generics,status
from datetime import datetime
from oosc.students.models import Students
from oosc.absence.serializers import DetailedAbsenceserializer
from oosc.attendance.serializers import AttendanceSerializer
from oosc.absence.models import Absence
from datetime import datetime
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
class ListCreateAttendance(generics.ListAPIView):
    queryset=Attendance.objects.all()
    serializer_class=AttendanceSerializer

class TakeAttendance(APIView):
    def post(self,request,format=None):
        now=str(datetime.now().date()).replace('-','')
        absents=[]
        print (request.data)
        try:
            for i in request.data["present"]:
                student=Students()
                student=Students.objects.filter(id=i)[0]
                student.total_absents=0
                student.last_attendance=datetime.now().date()
                abs = Absence.objects.filter(student=student, status=False)
                if(len(abs)>0):
                    print "reason for absence needed"
                    absents.append(student)
                student.save()
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
                student.total_absents = student.total_absents + 1
                if(student.total_absents>4):
                    abs=Absence.objects.filter(student=student,status=False)
                    if(len(abs)>0):
                        print ("found")
                        abs[0].date_to=datetime.now().date()
                        abs[0].save()
                    else:
                        ab=Absence()
                        ab.student=student
                        ab.date_to=datetime.now().date()
                        ab.date_from=student.last_attendance
                        ab.status=False
                        ab.save()
                else:
                    student.save()
                attendance = Attendance()
                attendance.date = datetime.now().date()
                attendance.id = now + str(i)
                attendance.status = 0
                attendance._class = student.class_id
                attendance.student = student
                attendance.save()
            print(absents)
            absnts=Absence.objects.filter(student__in=absents)
            ser=DetailedAbsenceserializer(absnts,many=True)
            return Response(data=ser.data,status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(data={"error":type(e),"error_description":e.message},status=status.HTTP_400_BAD_REQUEST)




