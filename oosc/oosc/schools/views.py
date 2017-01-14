from django.shortcuts import render
from oosc.schools.models import Schools
from rest_framework import generics
from oosc.schools.serializers import SchoolsSerializer
from rest_framework import status
from rest_framework.response import Response
from oosc.counties.models import Counties
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
            if(indx!=0):
                coun=Counties.objects.filter(county_name__contains=d[2])
                if(len(coun)>0):
                    print (coun[0].county_name)
                else:
                    cn=Counties()
                    cn.county_name=d[2]
                    cn.save()
                schs=Schools.objects.filter(emis_Code=d[1])
                if(len(schs)>0):
                    print (schs[0].school_name)
                else:
                    sch=Schools()
                    sch.school_name=d[5]
        return Response(data=data[1])


