from django.shortcuts import render
from oosc.attendance.models import Attendance
from rest_framework import generics,status
from datetime import datetime
from oosc.students.models import Students
from oosc.attendance.serializers import AbsentStudentSerializer
from oosc.absence.serializers import DetailedAbsenceserializer
from oosc.attendance.serializers import AttendanceSerializer
from oosc.absence.models import Absence
from datetime import datetime
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime,timedelta
from django_filters.rest_framework import FilterSet,DjangoFilterBackend
import django_filters
from django.db.models import Count,Case,When,IntegerField,Q,Value,CharField,TextField
from django.db.models.functions import ExtractMonth,ExtractYear,ExtractDay,TruncDate
from django.db.models.functions import Concat,Cast
from rest_framework import serializers


class AttendanceFilter(FilterSet):
    Class=django_filters.CharFilter(name="_class")
    date=django_filters.DateFilter(name="date")
    start_date = django_filters.DateFilter(name='date', lookup_expr=('gte'))
    end_date = django_filters.DateFilter(name='date', lookup_expr=('lte'))
    school=django_filters.NumberFilter(name="_class__school",)
    #date_range = django_filters.DateRangeFilter(name='date')
    class Meta:
        model=Attendance
        fields=['Class','date','start_date','end_date','_class',"school","student"]

class AbsenteesFilter(FilterSet):
    school = django_filters.NumberFilter(name="_class__school", )

    class Meta:
        model=Attendance
        fields=['date','school','_class']

class SerializerAll(serializers.Serializer):
    value=serializers.CharField()
    present_males=serializers.IntegerField()
    present_females=serializers.IntegerField(allow_null=True,)
    absent_males=serializers.IntegerField()
    absent_females=serializers.IntegerField()
    total=serializers.SerializerMethodField()
    def get_total(self,obj):
        total=obj["present_males"]+obj["present_females"]+obj["absent_males"]+obj["absent_females"]
        return total

    def to_representation(self, instance):
        # print instance,self.get_total(instance)
        stud = self.context.get("student")
        type = self.context.get("type")
        if stud:
            return {"present": instance["present_males"] + instance["present_females"],
                    "absent": instance["absent_males"] + instance["absent_females"],
                    "total": int(self.get_total(instance)), "value": instance["value"]}
        return super(SerializerAll, self).to_representation(instance)

class SerializerAllPercentages(serializers.Serializer):
    value=serializers.CharField()
    present_males=serializers.IntegerField(write_only=True)
    present_females=serializers.IntegerField(allow_null=True,write_only=True)
    absent_males=serializers.IntegerField(write_only=True)
    absent_females=serializers.IntegerField(write_only=True)
    total=serializers.SerializerMethodField()
    def get_total(self,obj):
        total=float(obj["present_males"]+obj["present_females"]+obj["absent_males"]+obj["absent_females"])
        return total
    def males_present(self,obj):
        return self.get_total(obj)
    def get_pm(self,obj,field):
        return round((obj[field]/self.get_total(obj))*100,2)
    def to_representation(self, instance):
        #print instance,self.get_total(instance)
        stud=self.context.get("student")
        type=self.context.get("type")
        if stud:
            return {"present":instance["present_males"]+instance["present_females"],"absent":instance["absent_males"]+instance["absent_females"],"total":int(self.get_total(instance)),"value":instance["value"]}
        return {"present_males":self.get_pm(instance,"present_males"),"present_females":self.get_pm(instance,"present_females"),
                "absent_males": self.get_pm(instance, "absent_males"),"absent_females": self.get_pm(instance, "absent_females"),
                "total":100,"value":instance["value"]}


class ListAbsentees(generics.ListAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AbsentStudentSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class=AbsenteesFilter

    def get_queryset(self):
        atts=Attendance.objects.filter(date__gte=datetime.now()-timedelta(days=7))
        atts=self.filter_queryset(atts)
        stds=self.get_absent_studs(data=atts)
        a=atts.filter(student_id__in=stds)
        d={}
        for x in a:
            d[x.student]=x
        att=d.values()
        return atts.filter(id__in=[g.id for g in att ])


    def get_absent_studs(self,data):
        r=Count(Case(When(status=0,then=1)))
        at = data.annotate(stud=Cast("student_id",output_field=IntegerField())).values("stud").annotate(absent=r).filter(absent__gte=3)
        return [st["stud"] for st in at]





class ListCreateAttendance(generics.ListAPIView):
    queryset=Attendance.objects.all()
    serializer_class=AttendanceSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class=AttendanceFilter

    def get_queryset(self):
        atts=Attendance.objects.all()
        atts=self.filter_queryset(atts)
        format = self.kwargs['type']
        at=self.get_formated_data(atts,format=format)
        #at["present_males"]=float(at["present_males"])/total
        return  at

    def get_serializer_context(self):
        print("setting the context")
        student = self.request.query_params.get('student', None)
        return {'type': self.kwargs['type'], "student": student}

    def get_serializer_class(self):
        if self.request.method == "GET":
            format = self.kwargs['type']
            if format != "daily":
                return SerializerAllPercentages
            return SerializerAll
        elif self.request.method == 'POST':
            return AttendanceSerializer

    def resp_fields(self):
        pm = Count(Case(When(Q(student__gender="M") & Q(status=1), then=1), output_field=IntegerField(), ))
        pf = Count(Case(When(Q(student__gender="F") & Q(status=1), then=1), output_field=IntegerField(), ))
        af = Count(Case(When(Q(student__gender="F") & Q(status=0), then=1), output_field=IntegerField(), ))
        am = Count(Case(When(Q(student__gender="M") & Q(status=0), then=1), output_field=IntegerField(), ))
        return pm,pf,af,am

    def get_formated_data(self,data,format):
        pm, pf, af, am=self.resp_fields()
        outp=Concat("month",Value(''),output_field=CharField())

        at = data.annotate(month=self.get_format(format=format)).values("month").annotate(present_males=pm, present_females=pf,
                                                                                absent_males=am, absent_females=af,value=outp)
        return at


    def get_format(self,format):
        daily=Concat(TruncDate("date"),Value(''),output_field=CharField(),)
        if(format=="monthly"):
            return Concat(Value('1/'),ExtractMonth('date'),Value('/'),ExtractYear("date"),output_field=CharField(),)
        elif format=="daily":
            return daily
        elif format== "yearly":
            return ExtractYear('date')
        elif format=="class":
            id=Cast("_class", output_field=TextField())
            return Concat("_class__class_name",Value(','),id,output_field=CharField())
        else:
            print daily
            return daily





class TakeAttendance(APIView):
    def post(self,request,format=None):
        now=self.request.data["date"].replace('-','')
        absents=[]
        thedate=self.request.data["date"]
        print (request.data)
        try:
            for i in request.data["present"]:
                print ("present")
                student=Students()
                student=Students.objects.filter(id=i)[0]
                student.total_absents=0
                student.last_attendance=datetime.now().date()
                abs = Absence.objects.filter(student=student, status=False)
                # if(len(abs)>0):
                #     print "reason for absence needed"
                #     absents.append(student)
                #     print "added to absents"
                # print student
                # student.save()
                attendance=Attendance()
                attendance.date=thedate
                attendance.id=now+str(i)
                attendance.status=1
                attendance._class=student.class_id
                attendance.student=student
                attendance.save()

                print (attendance.id)
            for i in request.data["absent"]:
                print ("Absemt")
                student = Students()
                student = Students.objects.filter(id=i)[0]
                # student.total_absents = student.total_absents + 1
                # if(student.total_absents>4):
                #     abs=Absence.objects.filter(student=student,status=False)
                #     if(len(abs)>0):
                #         print ("found")
                #         abs[0].date_to=datetime.now().date()
                #         abs[0].save()
                #     else:
                #         print ("saving ...")
                #         ab=Absence()
                #         ab.student=student
                #         ab.date_to=datetime.now().date()
                #         ab.date_from=student.last_attendance
                #         ab.status=False
                #         ab.save()
                #         print ("Saved ...")
                # else:
                #     print ("within ")
                #     student.save()
                attendance = Attendance()
                attendance.date = thedate
                attendance.id = now + str(i)
                attendance.status = 0
                attendance._class = student.class_id
                attendance.student = student
                attendance.save()
            print("Done replying")
            absnts=Absence.objects.filter(student__in=absents)
            #ser=DetailedAbsenceserializer(absnts,many=True)
            return Response(data=[],status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(data={"error":"Error","error_description":e.message},status=status.HTTP_400_BAD_REQUEST)

class WeeklyAttendanceReport(APIView):
    def get(self,request,format=None):
        fdate=datetime.now().date()
        ldate=fdate-timedelta(days=5)
        fdate=str(fdate)
        ldate=str(ldate)
        attends=Attendance.objects.filter(date__range=[ldate,fdate])
        presentmales=attends.filter(student__gender="M",status=1)
        presentfemales=attends.filter(student__gender="F",status=1)
        absentmales=attends.filter(student__gender="M",status=0)
        absentfemales=attends.filter(student__gender="F",status=0)
        pmales=len(presentmales)
        pmales=float(pmales)
        pfemales=float(len(presentfemales))
        amales=float(len(absentmales))
        afemales=float(len(absentfemales))
        total=float(pmales+pfemales+amales+afemales)
        ptotal=float(pmales+pfemales)
        atotal=float(amales+afemales)
        if(total==0):
            total=1
        print(pfemales,pmales,afemales,amales,total)

        return Response(data={"present":{"total":int((ptotal/total)*100),"males":int((pmales/total)*100),"females":int((pfemales/total)*100)},
                              "absent":{"total":int((atotal/total)*100),"males":int((amales/total)*100),"females":int((afemales/total)*100)}})

#class GraphAttendance()





