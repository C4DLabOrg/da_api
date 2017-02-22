from django.shortcuts import render
from oosc.students.models import Students
from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.views import APIView
from oosc.students.serializers import StudentsSerializer
from datetime import datetime,timedelta
import csv
from rest_framework import serializers
import json
from oosc.classes.models import Classes
from oosc.schools.models import Schools
from oosc.teachers.models import Teachers
from datetime import datetime
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

class ImportStudentSerializer(serializers.Serializer):
    fstname=serializers.CharField(max_length=50)
    midname=serializers.CharField(max_length=50,required=False,allow_null=True,allow_blank=True)
    lstname=serializers.CharField(max_length=50,required=False,allow_null=True,allow_blank=True)
    school=serializers.IntegerField()
    clas=serializers.CharField(max_length=50)
    gender=serializers.CharField(max_length=20)
    #date_enrolled=serializers.DateField(required=False,allow_null=True)
    # emis_code=serializers.IntegerField(required=False,allow_null=True)


def sew_class(s):
    s=s.split(' ')[1]
    if s=="ECD":
        return "Std 1"
    return "Std "+str(int(s)+1)

def set_class(s):
    return "Std "+s

def get_gender(s):
    if s.lower() =="male" or s.lower() == 'm':
        return "M"
    elif s.lower()=='female' or s.lower() == 'f':
        return "F"

def valid_date(date_text):
    try:
        datetime.strptime(date_text,'%Y-%m-%d')
        return True
    except ValueError:
        return False

class ImportStudents(APIView):
    def post(self,request,format=None):
        file=request.FILES["file"]
        data = [row for row in csv.reader(file.read().splitlines())]
        d=""
        s=0
        rowindex=[]
        err=""
        the_data=data[1:]
        for i,dat in enumerate(the_data):
            dt={"fstname":dat[6],"midname":dat[7],"lstname":dat[8], "school":dat[5],
                "clas":dat[13],"gender":dat[11]}
            ser=ImportStudentSerializer(data=dt)

            if ser.is_valid():
                sch=Schools.objects.filter(emis_code=ser.data.get("school"))
                teach=Teachers()
                if(sch.exists()):
                    sch=sch[0]
                    teach = Teachers.objects.filter(school=sch)
                    if(not teach.exists()):
                        return Response("Create atleast one Teacher for the school")
                    else:
                        teach=teach[0]
                else:
                    print (ser.data.get("school"))
                    return Response("Create School First")
                nxt_class=set_class(ser.data.get("clas"))
                if not nxt_class == "Std 9":
                    cls=Classes.objects.filter(class_name=nxt_class)
                    cl = Classes()
                    if(cls.exists()):
                        cl=cls[0]
                    else:
                        cl.class_name=nxt_class
                        cl.school=sch
                        cl.teacher=teach
                        cl.save()
                    std=Students.objects.filter(fstname=ser.data.get("fstname"),lstname=ser.data.get("lstname"),midname=ser.data.get("midname"),
                                                class_id=cl)
                    #check if student Exists
                    if(std.exists()):
                        #print "Found"
                        pass
                    else:
                        std=Students()
                        std.fstname=ser.data.get("fstname")
                        std.midname=ser.data.get("midname")
                        std.lstname=ser.data.get("lstname")
                        std.gender=get_gender(ser.data.get("gender"))
                        std.class_id=cl
                        if(valid_date(dat[2])):
                            std.date_enrolled=dat[2]
                        else:
                            std.date_enrolled=datetime.now()
                        std.save()
                        s += 1

                else:
                    print("Done Kcpe")
            else:
                err=ser.errors
            # schl=dat[5]
            # clas=dat[6]
            # if  clas and schl:
            #     pass
            # else:
            #     print dat
            #     return Response("Make Sure The Data is correct "+str(i)+" "+dat[6])
            # s=i
            # d=dat[4]
        f=s
        s=int((float(s)/float(len(the_data)))*100)
        rowindex.append({"name":"Import Summary","index":str(s)+"%, "+str(f)+" of  "+str(len(the_data))})
        rowindex.append({"name":"Errors","index":err})
        for i,dat in enumerate(data[0]):
            rw={'name':dat,'index':i}
            rowindex.append(rw)
        return Response(data=json.loads(json.dumps(rowindex)))