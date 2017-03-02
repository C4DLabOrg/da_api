from django.shortcuts import render
from oosc.students.models import Students
from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.views import APIView
from oosc.students.serializers import StudentsSerializer
from datetime import datetime,timedelta
from django_filters.rest_framework import FilterSet,DjangoFilterBackend
import django_filters
import csv
from rest_framework import serializers
import json
from oosc.classes.models import Classes
from oosc.schools.models import Schools
from oosc.teachers.models import Teachers
from datetime import datetime
from django.db.models import Count,Case,When,IntegerField,Q,Value,CharField,TextField
from django.db.models.functions import ExtractMonth,ExtractYear,ExtractDay,TruncDate
from django.db.models.functions import Concat,Cast
# Create your views here.

class ListCreateStudent(generics.ListCreateAPIView):
    queryset=Students.objects.all()
    serializer_class=StudentsSerializer

class EnrollmentFilter(FilterSet):
    school = django_filters.NumberFilter(name="class_id__school", )
    start_date = django_filters.DateFilter(name='date_enrolled', lookup_expr=('gte'))
    end_date = django_filters.DateFilter(name='date_enrolled', lookup_expr=('lte'))
    year=django_filters.NumberFilter(name="date_enrolled",lookup_expr=('year'))

    class Meta:
        model=Students
        fields=['class_id','gender','school','start_date','end_date','year']


class EnrollmentSerializer(serializers.Serializer):
    enrolled_males=serializers.IntegerField()
    enrolled_females=serializers.IntegerField()
    old_males=serializers.IntegerField()
    old_females=serializers.IntegerField()
    value=serializers.CharField()
    total=serializers.SerializerMethodField()
    def get_total(self,obj):
        return obj["enrolled_males"]+obj["enrolled_females"]+obj["old_males"]+obj["old_females"]
    def to_representation(self, instance):
        data = super(EnrollmentSerializer, self).to_representation(instance)
        return data

class GetEnrolled(generics.ListAPIView):
    serializer_class = EnrollmentSerializer
    queryset = Students.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_class = EnrollmentFilter



    def get_queryset(self):
        studs=self.filter_queryset(Students.objects.all())
        format = self.kwargs['type']
        at=self.get_formated_data(studs,format=format)


        return at

    def resp_fields(self):
        lst = str(datetime.now().date() - timedelta(days=365))
        enrolledm = Count(Case(When(Q(date_enrolled__gte=lst) & Q(gender="M"), then=1), output_field=IntegerField(), ))
        oldf = Count(Case(When(Q(gender="F") & Q(date_enrolled__lte=lst), then=1), output_field=IntegerField(), ))
        enrolledf = Count(Case(When(Q(gender="F") & Q(date_enrolled__gte=lst), then=1), output_field=IntegerField(), ))
        oldm = Count(Case(When(Q(gender="M") & Q(date_enrolled__lte=lst), then=1), output_field=IntegerField(), ))
        return enrolledm,oldf,enrolledf,oldm
    # def get(self,request,format=None):
    #     now=str(datetime.now().date()+timedelta(days=1))
    #     lst=str(datetime.now().date()-timedelta(days=365))
    #     studs=Students.objects.filter(date_enrolled__range=[lst,now])
    #
    #     females=studs.filter(gender='F')
    #     males=studs.filter(gender='M')
    #     return Response({"total":len(studs),"males":len(males),
    #                      "females":len(females)},status=status.HTTP_200_OK)
    def get_formated_data(self, data, format):
        enrolledm, oldf, enrolledf, oldm = self.resp_fields()
        outp = Concat("month", Value(''), output_field=CharField())
        at = data.annotate(month=self.get_format(format=format)).values("month").annotate(enrolled_males=enrolledm,
                                                                                          enrolled_females=enrolledf,
                                                                                          old_males=oldm,
                                                                                          old_females=oldf, value=outp).order_by('value')
        return at

    def get_format(self,format):
        daily=Concat(TruncDate("date_enrolled"),Value(''),output_field=CharField(),)
        monthly= Concat(Value('1/'), ExtractMonth('date_enrolled'), Value('/'), ExtractYear("date_enrolled"),
                      output_field=CharField(), )

        if(format=="monthly"):
            return monthly
        elif format=="daily":
            return daily
        elif format== "yearly":
            return ExtractYear('date_enrolled')
        elif format=="gender":
            return Concat(Value("gender"),Value(""),output_field=CharField())
        elif format=="school":
            id=Cast("class_id__school_id",output_field=TextField())
            return Concat("class_id__school__school_name",Value(','),id,output_field=CharField())
        elif format=="class":
            id=Cast("class_id", output_field=TextField())
            return Concat("class_id__class_name",Value(','),id,output_field=CharField())
        else:
            return monthly

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