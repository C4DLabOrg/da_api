from django.shortcuts import render
from oosc.students.models import Students
from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.views import APIView
from oosc.students.serializers import StudentsSerializer
from datetime import datetime,timedelta
# Create your views here.

class ListCreateStudent(generics.ListCreateAPIView):
    queryset=Students.objects.all()
    serializer_class=StudentsSerializer

class GetEnrolled(APIView):
    def get(self,request,format=None):
        now=str(datetime.now().date()+timedelta(days=1))
        lst=str(datetime.now().date()-timedelta(days=365))
        studs=Students.objects.filter(date_enrolled__range=[lst,now])
        ser=StudentsSerializer(studs,many=True)
        females=studs.filter(gender='F')
        males=studs.filter(gender='M')
        return Response({"total":len(studs),"males":len(males),
                         "females":len(females),"students":ser.data},status=status.HTTP_200_OK)