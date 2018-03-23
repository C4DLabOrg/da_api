from django.db.models.functions import Trunc
from django.http.response import HttpResponseBase
from django.shortcuts import render

from oosc.attendance.apps import attendance_taken
from oosc.attendance.models import Attendance, AttendanceHistory
from rest_framework import generics,status
from datetime import datetime
import pytz
from oosc.mylib.common import MyCustomException, get_list_of_dates
from oosc.stream.models import Stream
from oosc.stream.serializers import StreamSerializer
from oosc.stream.views import StreamFilter
from oosc.students.models import Students
from oosc.attendance.serializers import AbsentStudentSerializer, GetAttendanceHistorySerilizer
from oosc.absence.serializers import DetailedAbsenceserializer, AbsenceSerializer
from oosc.attendance.serializers import AttendanceSerializer
from oosc.absence.models import Absence
from oosc.attendance.permissions import IsTeacherOfTheSchool
from datetime import datetime
# Create your views here.
from bulk_update.helper import bulk_update
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime,timedelta
from django_subquery.expressions import Subquery,OuterRef
from django_filters.rest_framework import FilterSet,DjangoFilterBackend
import django_filters
from django.db.models import Count,Case,When,IntegerField,Q,Value,CharField,Sum,Avg,BooleanField,DateField,F
from django.db.models.functions import ExtractMonth,ExtractYear,ExtractDay,TruncDate
from django.db.models.functions import Concat,Cast
from rest_framework import serializers
from django.db import transaction
from rest_framework.pagination import PageNumberPagination
from django.utils.dateparse import parse_date

from oosc.teachers.views import str2bool

"""
from oosc.students.models import Students as St
from django.db.models import Count,Case,When,IntegerField,Q,Value,CharField,Sum,Avg,BooleanField
from django.db.models.functions import ExtractMonth,ExtractYear,ExtractDay,TruncDate
from django.db.models.functions import Concat,Cast

ot=list(St.objects.filter(class_id__school__emis_code__in=emis).values("class_id__school__emis_code").annotate(count=Count("class_id__school__emis_code")))


"""


class AttendanceHistoryFilter(FilterSet):
    Class=django_filters.CharFilter(name="_class")
    date=django_filters.DateFilter(name="date__date",)
    start_date = django_filters.DateFilter(name="date",lookup_expr="gte"  )
    end_date = django_filters.DateFilter(name='date', lookup_expr=('lte'))

    class Meta:
        model=AttendanceHistory
        fields=('id','start_date','date','end_date','_class',"Class")

class AttendanceFilter(FilterSet):
    Class=django_filters.CharFilter(name="_class")
    date=django_filters.DateFilter(name="date__date",)
    start_date = django_filters.DateFilter(name="date",lookup_expr="gte"  )
    end_date = django_filters.DateFilter(name='date', lookup_expr=('lte'))
    school=django_filters.NumberFilter(name="_class__school",)
    year=django_filters.NumberFilter(name="date__year")
    month=django_filters.NumberFilter(name="date__month")
    county=django_filters.NumberFilter(name="_class__school__zone__subcounty__county",method="filter_county")
    partner=django_filters.NumberFilter(name="partner",method="filter_partner")
    partner_admin=django_filters.NumberFilter(name="partner",method="filter_partner_admin",label="Partner Admin Id")
    county_name=django_filters.CharFilter(name="_class__school__zone__subcounty__county__county_name",lookup_expr="icontains")
    is_oosc=django_filters.CharFilter(name="student__is_oosc",method="filter_is_oosc")

    #date_range = django_filters.DateRangeFilter(name='date')
    class Meta:
        model=Attendance
        fields=['Class','date','start_date','year','end_date','is_oosc','_class',"school","student","county","partner","county_name"]

    def filter_partner(self, queryset, name, value):
        return queryset.filter(_class__school__partners__id=value)

    def filter_is_oosc(self, queryset, name, value):
        return queryset.filter(student__is_oosc=str2bool(value))

    def filter_county(self,queryset,name,value):
        return queryset.exclude(Q(student__class_id__school__zone=None) | Q(student__class_id__school__subcounty=None)).filter(Q(student__class_id__school__zone__subcounty__county=value) | Q(student__class_id__school__subcounty__county=value))



    def filter_partner_admin(self, queryset, name, value):
        return queryset.filter(_class__school__partners__partner_admins__id=value)

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
        # #print instance,self.get_total(instance)
        stud = self.context.get("student")
        type = self.context.get("type")
        if stud  :
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

    def get_males_total(self,obj):
        return float(obj["present_males"]+obj["absent_males"])

    def get_gender_total(self,obj,field):
        #Get the gender from
        gender=field.split("_")[-1]
        return float(obj["present_"+gender] + obj["absent_"+gender])

    def get_total(self,obj):
        total=float(obj["present_males"]+obj["present_females"]+obj["absent_males"]+obj["absent_females"])
        return total

    def males_present(self,obj):
        return self.get_total(obj)

    def get_percentage(self,obj,field):
        total=obj[field+"_females"]+obj[field+"_males"]
        if total ==0:return 0
        return round((total/self.get_total(obj))*100,2)

    def get_pm(self,obj,field):
        if self.get_gender_total(obj,field=field) ==0:
            return 0
        return round((obj[field]/self.get_gender_total(obj,field=field))*100,2)
        # return round((obj[field]/self.get_total(obj))*100,2)

    def to_representation(self, instance):
        ##print instance,self.get_total(instance)
        stud=self.context.get("student")
        type=self.context.get("type")
        return_type=self.context.get("return_type")
        # print ("return type",return_type)
        if stud or return_type == "count":
            return {"present":instance["present_males"]+instance["present_females"],"absent":instance["absent_males"]+instance["absent_females"],"total":int(self.get_total(instance)),"value":instance["value"]}
        return {"present_males":self.get_pm(instance,"present_males"),"present_females":self.get_pm(instance,"present_females"),
                "absent_males": self.get_pm(instance, "absent_males"),"absent_females": self.get_pm(instance, "absent_females"),
                "present":self.get_percentage(instance,"present"),"absent":self.get_percentage(instance,"absent"),
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

class StandardresultPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 1000
    page_size_query_param = 'page_size'



def days_between(d1, d2):
    try:
        d1 = datetime.strptime(d1, "%Y-%m-%d")
        d2 = datetime.strptime(d2, "%Y-%m-%d")
        return abs((d2 - d1).days)
    except ValueError:
        ##Return a big number if either of the dates has an error
        return 100000



class ListCreateAttendance(generics.ListAPIView):
    queryset=Attendance.objects.all()
    serializer_class=AttendanceSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class=AttendanceFilter
    pagination_class = StandardresultPagination
    nonefomats = ["yearly", "class","monthly","gender","county","oosc"]
    fakepaginate=False

    def paginate_queryset(self, queryset):
        if self.paginator is None:
            return None
        theformat = self.kwargs['type']
        startdate=self.request.query_params.get('start_date', "2017-04-01")
        enddate=self.request.query_params.get('end_date', datetime.now().strftime("%Y-%m-%d"))
        pagesize=int(self.request.query_params.get('page_size', 200))
        if theformat in self.nonefomats:
            self.fakepaginate=True
            return None
        elif startdate !=None and days_between(startdate,enddate) <= pagesize:
            # print (days_between(startdate,enddate),days_between(startdate,enddate) <= pagesize)
            self.fakepaginate = True
            return None
        elif theformat=="weekly" and startdate !=None and days_between(startdate,enddate)/5 <=pagesize:
            # print ("weekly",days_between(startdate, enddate)/5, days_between(startdate, enddate)/5 <= pagesize)
            self.fakepaginate = True
            return None
        return  self.paginator.paginate_queryset(queryset, self.request, view=self)

    def finalize_response(self, request, response, *args, **kwargs):
        assert isinstance(response, HttpResponseBase), (
            'Expected a `Response`, `HttpResponse` or `HttpStreamingResponse` '
            'to be returned from the view, but received a `%s`'
            % type(response)
        )

        #If it does not use pagination and require fake pagination for response
        if self.fakepaginate:
            data=response.data
            resp={}
            resp["count"]=len(data)
            resp["next"]=None
            resp["prev"]=None
            resp["results"]=data
            response.data=resp
        # print (response.data)
        if isinstance(response, Response):
            if not getattr(request, 'accepted_renderer', None):
                neg = self.perform_content_negotiation(request, force=True)
                request.accepted_renderer, request.accepted_media_type = neg
            response.accepted_renderer = request.accepted_renderer
            response.accepted_media_type = request.accepted_media_type
            response.renderer_context = self.get_renderer_context()

        for key, value in self.headers.items():
            response[key] = value
        return response
    # def get_pagination_class(self):
    #     print("Getting the format")
    #     theformat = self.kwargs['type']
    #     nonefomats=["yearly","class"]
    #     if theformat in nonefomats:
    #         return None
    #     return StandardresultPagination

    # def list(self, request, *args, **kwargs):

    def list(self, request, *args, **kwargs):
        queryset = self.get_my_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


    def get_my_queryset(self):
        # atts=Attendance.objects.all()
        atts=Attendance.objects.select_related("student","_class")
        atts=self.filter_queryset(atts)
        format = self.kwargs['type']
        at=self.get_formated_data(atts,format=format)
        #at["present_males"]=float(at["present_males"])/total

        return at

    def get_serializer_context(self):
        ####print("setting the context")
        student = self.request.query_params.get('student', None)
        return_type = self.request.query_params.get('return_type', None)
        return {'type': self.kwargs['type'], "student": student,"return_type":return_type}

    def get_serializer_class(self):
        if self.request.method == "GET":
            format = self.kwargs['type']
            if format != "daily":
                return SerializerAllPercentages
            return SerializerAll
        elif self.request.method == 'POST':
            return AttendanceSerializer

    def resp_fields(self):
        pm = Count(Case(When(Q(student__gender="M") & Q(status=1) & Q(student__active=True), then=1), output_field=IntegerField(), ))
        pf = Count(Case(When(Q(student__gender="F") & Q(status=1) & Q(student__active=True), then=1), output_field=IntegerField(), ))
        af = Count(Case(When(Q(student__gender="F") & Q(status=0)& Q(student__active=True), then=1), output_field=IntegerField(), ))
        am = Count(Case(When(Q(student__gender="M") & Q(status=0)& Q(student__active=True), then=1), output_field=IntegerField(), ))
        return pm,pf,af,am

    def get_formated_data(self,data,format):
        pm, pf, af, am=self.resp_fields()

        outp=Concat("month",Value(''),output_field=CharField())

        at = data.annotate(month=self.get_format(format=format)).values("month")

        at=at.annotate(present_males=pm, present_females=pf,absent_males=am, absent_females=af,value=F("month"))
        #at=at.annotate(value=Concat(Value(queryet),Value(""),output_field=CharField()))
        # #print (at)
        at=at.exclude(present_males=0,present_females=0,absent_males=0,absent_females=0)

        return self.filter_formatted_data(format=format,data=at)


    def filter_formatted_data(self,format,data):
        if format=="monthly":
            return sorted(data,key=lambda x: parse_date(x["value"]),reverse=True)
        return data.order_by("value")


    def get_format(self,format):
        daily=Concat(TruncDate("date"),Value(''),output_field=CharField(),)
        weekly=Concat(Trunc("date","week"),Value(''),output_field=CharField(),)
        if(format=="monthly"):
            return Concat(ExtractYear("date"),Value('-'),ExtractMonth('date'),Value('-1'),output_field=DateField(),)
        elif format=="daily":
            return daily
        elif format=="weekly":
            return weekly
        elif format== "yearly":
            return ExtractYear('date')
        elif format == "stream":
            return Concat("_class__class_name", Value(''), output_field=CharField())
        elif format =="county":
            return Concat("_class__school__zone__subcounty__county__county_name",Value(''),output_field=CharField())
        elif format=="class":
            return Concat("_class___class",Value(''),output_field=CharField())
        elif format=="oosc":
            return Concat("student__is_oosc",Value(''),output_field=BooleanField())
        elif format=="gender":
            return Value("gender",output_field=CharField())
            # return Concat("student__gender",Value(""),output_field=CharField())
        else:
            # #print daily
            return daily


class TakeAttendance(APIView):
    permission_classes = (IsTeacherOfTheSchool,)

    def send_attendance(self, present, absent,date,_class):
        attendance_taken.send(sender=self.__class__, _class=_class,absent=absent,present=present,date=date)

    def post(self,request,format=None):
        now=self.request.data["date"].replace('-','')
        absents=[]
        thedate=self.request.data["date"]
        #print (request.data)
        classid=None
        pres=len(request.data["present"])
        abss=len(request.data["absent"])
        date=thedate
        dclassid=None
        try:
            with transaction.atomic():
                for i in request.data["present"]:
                    #print ("present")
                    student=Students()
                    student=Students.objects.filter(id=i)[0]
                    student.total_absents=0

                    ###send the
                    if student.class_id !=dclassid:
                        dclassid=student.class_id
                        self.send_attendance(present=pres,absent=abss,date=date,_class=student.class_id_id)


                    student.last_attendance=datetime.now().date()
                    abs = Absence.objects.filter(student=student, status=False)
                    # if(len(abs)>0):
                    #     #print "reason for absence needed"
                    #     absents.append(student)
                    #     #print "added to absents"
                    # #print student
                    # student.save()
                    attendance=Attendance()
                    attendance.date=thedate
                    attendance.id=now+str(i)
                    attendance.status=1
                    attendance._class=student.class_id
                    if student.class_id != None:classid=student.class_id
                    attendance.student=student
                    attendance.save()

                    #print (attendance.id)
                for i in request.data["absent"]:
                    #print ("Absemt")
                    student = Students()

                    student = Students.objects.filter(id=i)[0]

                    ###send the
                    if student.class_id != dclassid:
                        dclassid = student.class_id
                        self.send_attendance(present=pres, absent=abss, date=date, _class=student.class_id_id)

                    # student.total_absents = student.total_absents + 1
                    # if(student.total_absents>4):
                    #     abs=Absence.objects.filter(student=student,status=False)
                    #     if(len(abs)>0):
                    #         #print ("found")
                    #         abs[0].date_to=datetime.now().date()
                    #         abs[0].save()
                    #     else:
                    #         #print ("saving ...")
                    #         ab=Absence()
                    #         ab.student=student
                    #         ab.date_to=datetime.now().date()
                    #         ab.date_from=student.last_attendance
                    #         ab.status=False
                    #         ab.save()
                    #         #print ("Saved ...")
                    # else:
                    #     #print ("within ")
                    #     student.save()
                    attendance = Attendance()
                    attendance.date = thedate
                    attendance.id = now + str(i)
                    attendance.status = 0
                    attendance._class = student.class_id
                    if student.class_id != None:classid=student.class_id
                    attendance.student = student
                    attendance.save()
            ####print("Done replying")
            ##Get the students with an open absence record
            absnts=DetailedAbsenceserializer(Absence.objects.filter(student_id__in=request.data["absent"],status=True),many=True)
            #Update attendance has been taken for the class
            print("Finalizing .... %s"%(classid))
            classid.attendance_taken(thedate)
            # if Stream.objects.filter(id=classid).exists():
            #     cl=Stream.objects.filter(id=classid)[0]
            #     cl.attendance_taken(thedate)
            return Response(data=absnts.data,status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(data={"error":"Error","error_description":e.message},status=status.HTTP_400_BAD_REQUEST)


class AttendanceHistorySerializer(object):
    pass


class MonitoringAttendanceTaking(generics.ListAPIView):
    queryset = Stream.objects.all()
    serializer_class = GetAttendanceHistorySerilizer
    filter_backends = (DjangoFilterBackend,)
    filter_class=StreamFilter
    pagination_class = StandardresultPagination
    allowed_order_by=["school","attendance_count"]

    def get_queryset(self):
        start_date,end_date,attendance_taken=self.parse_querparams()
        print ('%s to %s'%(start_date,end_date))

        ###Get the days attendace was expected
        days=get_list_of_dates(start_date=start_date,end_date=end_date)
        total_days=len(days)
        # print (total_days)

        ###Get order by
        order_by=self.request.GET.get("order_by",None)
        if order_by not in self.allowed_order_by:order_by="attendance_count"

        atts=AttendanceHistory.objects.all()
        streams=self.filter_queryset(self.queryset)
        atts=atts.filter(_class_id=OuterRef("id")).filter(date__in=days).annotate(theclass=F("_class")).values("_class").\
            annotate(count=Count("_class")).values_list("count",flat=True)

        ###Annoatate the data
        streams=streams.annotate(attendance_count=Subquery(atts[:1],output_field=IntegerField()),
                                 total_days=Value(total_days,output_field=IntegerField()),
                                 school_name=F("school__school_name"),
                              school_type=F("school__status"),
                              school_emis_code=F("school__emis_code"),
                                 ).values("id","attendance_count","class_name","total_days","school_name","school_emis_code","school_type")\


        ###Order_by
        if order_by =="school":
            streams=streams.order_by("school_name","-attendance_count","class_name")
        else:
            streams = streams.order_by( "-attendance_count","school_name","class_name")




        print (attendance_taken)
        if  attendance_taken:
            return streams.filter(attendance_count__gte=0)
        else:
            return streams.filter(attendance_count__isnull=True)


    # def list(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()
    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(queryset)
    #
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(queryset)

    def parse_querparams(self):
        start_date = self.request.GET.get("start_date", None)
        end_date = self.request.GET.get("end_date", None)
        taken_attendance = self.request.GET.get("taken_attendance", None)
        if start_date == None or end_date == None or taken_attendance ==None: raise MyCustomException(
            "You must include the `start_date` , `end_date` , `taken_attendance` in the query params");
        print ("taken_attendance",taken_attendance)
        return start_date,end_date,str2bool(taken_attendance)

class WeeklyAttendanceReport(APIView):
    def get(self,request,format=None):
        fdate=datetime.now().date()
        ldate=fdate-timedelta(days=5)
        fdate=str(fdate)
        ldate=str(ldate)
        attends=Attendance.objects.filter(date__range=[ldate,fdate])
        presentmales=attends.filter(student__gender="M",status=1,student__active=True)
        presentfemales=attends.filter(student__gender="F",status=1,student__active=True)
        absentmales=attends.filter(student__gender="M",status=0,student__active=True)
        absentfemales=attends.filter(student__gender="F",status=0,student__active=True)
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
        ####print(pfemales,pmales,afemales,amales,total)

        return Response(data={"present":{"total":int((ptotal/total)*100),"males":int((pmales/total)*100),"females":int((pfemales/total)*100)},
                              "absent":{"total":int((atotal/total)*100),"males":int((amales/total)*100),"females":int((afemales/total)*100)}})

#class GraphAttendance()





