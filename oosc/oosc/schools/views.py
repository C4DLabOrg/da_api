from django.shortcuts import render
from oosc.schools.models import Schools
from rest_framework import generics
from oosc.schools.serializers import SchoolsSerializer
from rest_framework import status
from rest_framework.response import Response
from oosc.counties.models import Counties
from oosc.subcounty.models import SubCounty
from oosc.zone.models import Zone
from oosc.teachers.models import Teachers
from oosc.students.models import Students
from django.http import Http404
from django_filters.rest_framework import FilterSet,DjangoFilterBackend
import django_filters

from django.conf import settings
import csv,codecs
from rest_framework.permissions import IsAdminUser
# Create your views here.
from rest_framework.views import APIView
from django.core.files.storage import FileSystemStorage

class ListCreateSchool(generics.ListCreateAPIView):
    queryset=Schools.objects.all();
    serializer_class=SchoolsSerializer
    #permission_classes = (IsAdminUser,)
def mycsv_reader(csv_reader):
  while True:
    try:
      yield next(csv_reader)
    except csv.Error:
      # error handling what you want.
      pass
    continue
  return



class ImportSchools(APIView):
    def post(self,request,format=None):
        file=request.FILES["file"]
        data = [row for row in csv.reader(file.read().splitlines())]
        for indx,d in enumerate(data):
            print indx
            if(indx>22190):
                ##Check if county present
                coun=Counties.objects.filter(county_name__contains=d[2])
                cn = Counties()
                if(len(coun)>0):
                    print (coun[0].county_name)
                    cn=coun[0]
                else:
                    cn.county_name=d[2]
                    cn.save()
                #Check if subcounty present in db
                sub=SubCounty.objects.filter(name__contains=d[3])
                su = SubCounty()
                if(len(sub)>0):
                    print (sub[0].name)
                    su=sub[0]
                else:
                    su.county=cn
                    su.name=d[3]
                    su.save()
                #check if zone present in db
                zones=Zone.objects.filter(name__contains=d[4])
                zone = Zone()
                if(len(zones)>0):
                    print (zones[0].name)
                    zone=zones[0]
                else:

                    zone.county=cn
                    zone.subcounty=su
                    zone.name=d[4]
                    zone.save()
                #Schools
                schs=Schools.objects.filter(emis_code=d[1])
                sch = Schools()
                if(len(schs)>0):
                    print (schs[0].school_name)
                    sch = schs[0]
                else:
                    sch.school_name=d[5]
                    sch.zone=zone
                    sch.level=d[6].upper()
                    sch.status=d[7].upper()
                    sch.emis_code=d[1]
                    sch.save()
        return Response(data=data[1])

class SearchEmiscode(generics.RetrieveAPIView):
    queryset = Schools.objects.all()
    serializer_class = SchoolsSerializer

    def get_object(self):
        emiscode = self.kwargs['emiscode']
        sch=Schools.objects.filter(emis_code=emiscode)
        if(sch.exists()):
            return sch[0]
        raise Http404


class GetAllReport(APIView):

    def get(self,request,format=None):
        students=Students.objects.all()
        mstudents=students.filter(gender="M")
        fstudents=students.filter(gender="F")
        mstudents=len(mstudents)
        fstudents=len(fstudents)
        schools=len(Schools.objects.all())
        teachers=len(Teachers.objects.all())
        return Response(data={"schools":schools,"teachers":teachers,"students":{"males":mstudents,"females":fstudents}})



