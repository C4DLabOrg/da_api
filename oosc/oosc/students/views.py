import operator
from django.contrib.auth.models import User,Group
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction
from django.http.response import HttpResponseBase
from django.shortcuts import render
import json

from django.templatetags.static import static
from django_subquery.expressions import OuterRef, Subquery
from rest_framework.exceptions import APIException

from oosc.attendance.views import AbsenteesFilter, AttendanceFilter
from oosc.mylib.common import filter_students_by_names, MyCustomException, get_stream_name_regex, get_list_of_dates
from oosc.mylib.excel_export import excel_generate
from oosc.mylib.queryset2excel import exportcsv
from oosc.students.models import Students,ImportError,ImportResults
from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.views import APIView
from oosc.students.serializers import StudentsSerializer, ImportErrorSerializer, ImportResultsSerializer, \
    SimpleStudentSerializer, SimplerStudentSerializer, StudentsUpdateOoscSerializer
from datetime import datetime,timedelta
from django_filters.rest_framework import FilterSet,DjangoFilterBackend
import django_filters
import csv
from oosc.students.permissions import IsTeacherOrAdmin, IsTeacherOrPartner
from rest_framework import serializers
import json
from oosc.stream.models import Stream
from oosc.schools.models import Schools
from oosc.teachers.models import Teachers
from datetime import datetime
from django.db.models import Count,Case,When,IntegerField,Q,Value,CharField,TextField,F, DateField
from django.db.models.functions import ExtractMonth,ExtractYear,ExtractDay,TruncDate
from django.db.models.functions import Concat,Cast
from rest_framework.response import Response
from rest_framework import status
from oosc.history.models import History
from oosc.attendance.models import Attendance
from rest_framework.pagination import PageNumberPagination
# Create your views here.
from oosc.partner.models import Partner
from sys import stdout
from django.utils.dateparse import parse_date

from oosc.teachers.views import str2bool


class StudentFilter(FilterSet):
    name = django_filters.CharFilter(name="student__name", method="filter_name",label="First Name | Middle Name | Last Name")
    Class=django_filters.NumberFilter(name="class_id",label="Stream Id")
    school=django_filters.NumberFilter(name="class_id__school",label="School Id")
    school_emis_code=django_filters.NumberFilter(name="class_id__school__emis_code", label="School emis code")
    partner=django_filters.NumberFilter(name="",label="Partner  Id",method="filter_partner")
    partner_admin=django_filters.NumberFilter(name="",label="Partner Admin Id",method="filter_partner_admin")
    county = django_filters.NumberFilter(name="class_id__school__zone__subcounty__county_id", label="County Id")
    birth_start_date = django_filters.DateFilter(name="date_of_birth", lookup_expr="gte")
    birth_end_date = django_filters.DateFilter(name='date_of_birth', lookup_expr=('lte'))
    enrolled_start_date = django_filters.DateFilter(name="date_enrolled", lookup_expr="gte")
    enrolled_end_date = django_filters.DateFilter(name='date_enrolled', lookup_expr=('lte'))



    class Meta:
        model=Students
        fields=('name','fstname','birth_start_date','birth_end_date','enrolled_start_date','enrolled_end_date','midname','lstname','admission_no','partner','gender','active','school','school_emis_code','county','is_oosc','graduated')

    def filter_name(self,queryset,name,value):
        return filter_students_by_names(queryset,value)

    def filter_partner_admin(self,queryset,name,value):
        return  queryset.filter(class_id__school__partners__partner_admins__id=value)

    def filter_partner(self, queryset, name, value):
        return queryset.filter(class_id__school__partners__id=value)


class StandardresultPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 1000
    page_size_query_param = 'page_size'

class ListCreateStudent(generics.ListCreateAPIView):
    queryset=Students.objects.select_related("class_id","class_id__school")
    serializer_class=StudentsSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class=StudentFilter
    pagination_class = StandardresultPagination

    def perform_create(self, serializer):
        #obj=self.get_object()
        stud=serializer.save()
        hist=History()
        hist.student=stud
        hist._class=stud.class_id
        hist.joined=stud.date_enrolled
        if stud.not_in_school_before:
            hist.joined_description="Not in School Before"
        else:
            hist.joined_description="In school before"
        hist.save()


class DeleteSerializer(serializers.Serializer):
    reason=serializers.CharField(max_length=20,required=True)

class RetrieveUpdateStudent(generics.RetrieveUpdateDestroyAPIView):
    queryset=Students.objects.all()
    serializer_class=StudentsSerializer

    def get_serializer_class(self):
        if self.request.method=="DELETE":
            return DeleteSerializer
        return StudentsSerializer


    def perform_update(self, serializer):
        obj=self.get_object()
        if obj.class_id !=serializer.validated_data.get("class_id"):
            stud=obj
            hist = History()
            hist.student = stud
            hist._class = serializer.validated_data.get("class_id")
            hist.joined = stud.date_enrolled
            hist.joined_description="Class Change"
            hist.save()
            serializer.save(previous_class=obj.class_id_id)
        else:
            serializer.save()



    def delete(self, request, *args, **kwargs):
        params=self.request.query_params
        ser=DeleteSerializer(data=params)
        if not ser.is_valid():
            return Response(ser.errors,status=status.HTTP_400_BAD_REQUEST)
        object=self.get_object()

        if(ser.data["reason"].lower() == "error"):
            object.delete()
            return Response("",status=status.HTTP_204_NO_CONTENT);
        object.deactivate(ser.data["reason"])
        object.save()
        hist=History.objects.filter(student=object,_class=object.class_id)
        if(hist.exists()):
            hist=hist[0]
            hist.left=datetime.now()
            hist.left_description=ser.data["reason"]
        else:
            stud=object
            hist=History()
            hist.student = stud
            hist._class = stud.class_id
            hist.left = datetime.now()
            hist.left_description=ser.data["reason"]
            hist.save()
        return Response("",status=status.HTTP_204_NO_CONTENT)

class EnrollmentFilter(FilterSet):
    Class = django_filters.NumberFilter(name="class_id", label="Stream Id")
    school = django_filters.NumberFilter(name="class_id__school", label="School Id")
    school_emis_code = django_filters.NumberFilter(name="class_id__school__emis_code", label="School emis code")
    start_date = django_filters.DateFilter(name='date_enrolled', lookup_expr=('gte'))
    end_date = django_filters.DateFilter(name='date_enrolled', lookup_expr=('lte'))
    year=django_filters.NumberFilter(name="date_enrolled",lookup_expr=('year'))
    partner = django_filters.NumberFilter(name="partner", label="Partner Id", method="filter_partner")
    class Meta:
        model=Students
        fields=['class_id','gender','is_oosc','school','start_date','end_date','year']

    def filter_partner(self, queryset, name, value):
        return queryset.filter(class_id__school__partners__id=value)


class EnrollmentSerializer(serializers.Serializer):
    enrolled_males=serializers.IntegerField()
    enrolled_females=serializers.IntegerField()
    dropout_enrolled_males=serializers.IntegerField()
    dropout_enrolled_females=serializers.IntegerField()
    old_males=serializers.IntegerField()
    old_females=serializers.IntegerField()
    dropout_old_males = serializers.IntegerField()
    dropout_old_females = serializers.IntegerField()
    value=serializers.CharField()
    total=serializers.SerializerMethodField()
    active_total=serializers.SerializerMethodField()
    dropout_total=serializers.SerializerMethodField()

    def get_total(self,obj):
        return obj["enrolled_males"]+obj["enrolled_females"]+obj["old_males"]+obj["old_females"] + obj["dropout_enrolled_males"]+obj["dropout_enrolled_females"]+obj["dropout_old_males"]+obj["dropout_old_females"]

    def get_active_total(self,obj):
        return obj["enrolled_males"]+obj["enrolled_females"]+obj["old_males"]+obj["old_females"]

    def get_dropout_total(self,obj):
        return  obj["dropout_enrolled_males"]+obj["dropout_enrolled_females"]+obj["dropout_old_males"]+obj["dropout_old_females"]

    def to_representation(self, instance):
        # data = super(EnrollmentSerializer, self).to_representation(instance)
        return instance

class GetEnrolled(generics.ListAPIView):
    serializer_class = EnrollmentSerializer
    queryset = Students.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_class = EnrollmentFilter
    pagination_class = None
    nonefomats = [ "class","gender", "county"]
    fakepaginate = False

    def list(self, request, *args, **kwargs):
        queryset = self.get_my_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_my_queryset(self):
        studs=self.filter_queryset(Students.objects.all())
        format = self.kwargs['type']
        at=self.get_formated_data(studs,format=format)
        # print(at)
        return at

    def resp_fields(self):
        #lst = str(datetime.now().date() - timedelta(days=365))
        #enrolledm = Count(Case(When(Q(date_enrolled__gte=lst) & Q(gender="M"), then=1), output_field=IntegerField(), ))
        enrolledm = Case(
            When(Q(is_oosc=False) & Q(gender="F") & Q(active=False), then=Value("dropout_old_females")),
            When(Q(is_oosc=False) & Q(gender="M") & Q(active=False), then=Value("dropout_old_males")),
            When(Q(is_oosc=False) & Q(gender="M") & Q(active=False), then=Value("dropout_old_males")),
            When((Q(is_oosc=True) & Q(gender="M") & Q(active=False)), then=Value("dropout_enrolled_males")),
            When(Q(is_oosc=True) & Q(active=False) & Q(gender="F"), then=Value("dropout_enrolled_females")),
            When(Q(is_oosc=True) & Q(gender="M" ) & Q(active=True), then=Value("enrolled_males")),
            When(Q(is_oosc=True) & Q(gender="F" ) & Q(active=True), then=Value("enrolled_females")),
            When(Q(is_oosc=False) & Q(gender="F" ) & Q(active=True), then=Value("old_females")),
            When(Q(is_oosc=False) & Q(gender="M" ) & Q(active=True), then=Value("old_males")),
            default=Value("others")
            ,output_field=CharField()
        )

        return enrolledm

    # def resp_fields(self):
    #     #lst = str(datetime.now().date() - timedelta(days=365))
    #     #enrolledm = Count(Case(When(Q(date_enrolled__gte=lst) & Q(gender="M"), then=1), output_field=IntegerField(), ))
    #     enrolledm = Count(Case(When(Q(is_oosc=True) & Q(gender="M" ) & Q(active=True), then=1), output_field=IntegerField(), ))
    #     oldf = Count(Case(When(Q(gender="F") & Q(is_oosc=False)& Q(active=True) , then=1), output_field=IntegerField(), ))
    #     enrolledf = Count(Case(When(Q(gender="F") & Q(is_oosc=True) & Q(active=True), then=1), output_field=IntegerField(), ))
    #     oldm = Count(Case(When(Q(gender="M") & Q(is_oosc=False) & Q(active=True) , then=1), output_field=IntegerField(), ))
    #     dropoldm = Count(Case(When(Q(gender="M") & Q(is_oosc=False) &  Q(active=False), then=1), output_field=IntegerField(), ))
    #     dropoldf = Count(Case(When(Q(gender="F") & Q(is_oosc=False)& Q(active=False), then=1), output_field=IntegerField(), ))
    #     dropnewm = Count(Case(When((Q(gender="M") & Q(is_oosc=True)& Q(active=False)), then=1), output_field=IntegerField(), ))
    #     dropnewf = Count(Case(When(Q(gender="F") & Q(is_oosc=True)& Q(active=False), then=1), output_field=IntegerField(), ))
    #
    #     return enrolledm,oldf,enrolledf,oldm,dropoldm,dropoldf,dropnewm,dropnewf

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
        enrolledm= self.resp_fields()
        # enrolledm, oldf, enrolledf, oldm,dropoldm,dropoldf,dropnewm,dropnewf = self.resp_fields()
        outp = Concat("month", Value(''), output_field=CharField())
        at = data.annotate(month=self.get_format(format=format)).values("month") \
            .order_by('month','type').annotate(type=enrolledm).annotate(count=Count("type"))
        return self.filter_formatted_data(format=format,data=at)

    def filter_formatted_data(self,format,data):
        # if format=="monthly":
        #     print("Sorting the monthlyv data .")
        #     return sorted(data,key=lambda x: parse_date(x["month"]),reverse=True)
        return data.order_by("month")


    def group(self,data):
        data_dict=json.loads(json.dumps(data))
        values=[d["month"] for d in data_dict]
        values=list(set(values))
        output=[]
        for a in values:
            if a =="":continue
            value_obj = {}
            value_obj["value"] = a
            #Try getting the value object
            value_objs=[p for p in data_dict if p["month"] == a]
            total_attrs=["old_males","old_females","enrolled_males","enrolled_females"]
            dropout_total_attrs=["dropout_old_males","dropout_old_females","dropout_enrolled_males","dropout_enrolled_females"]
            dropout_total=0
            total=0
            for b in value_objs:
                if b["type"] in total_attrs :
                    total+=b["count"]
                elif b["type"] in dropout_total_attrs:
                  dropout_total+=b["count"]
                value_obj[b["type"]]=b["count"]
            value_obj["total"]=total
            value_obj["dropout_total"]=dropout_total
            output.append(self.confirm_obj(value_obj))

        return sorted(output,key= lambda k:k.get('value',0),reverse=False)

    def confirm_obj(self,obj):
        attrs=["dropout_old_females","dropout_old_males","dropout_enrolled_females"
            ,"dropout_enrolled_males","old_males","old_females","enrolled_males","enrolled_females"]
        for at in attrs:
            try:
                obj[at]
            except:
                obj[at]=0

        return obj

    def paginate_queryset(self, queryset):
        self.fakepaginate=True
        return None
        # if self.paginator is None:
        #     return None
        # theformat = self.kwargs['type']
        # if theformat in self.nonefomats:
        #     self.fakepaginate = True
        #     return None
        # return self.paginator.paginate_queryset(queryset, self.request, view=self)



    def finalize_response(self, request, response, *args, **kwargs):
        assert isinstance(response, HttpResponseBase), (
            'Expected a `Response`, `HttpResponse` or `HttpStreamingResponse` '
            'to be returned from the view, but received a `%s`'
            % type(response)
        )
        response.data=self.group(response.data)
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

    def get_format(self,format):
        daily=Concat(TruncDate("date_enrolled"),Value(''),output_field=CharField(),)
        monthly= Concat(ExtractYear("date_enrolled"), Value('-'), ExtractMonth('date_enrolled'), Value('-1'), output_field=DateField(), )

        # monthly= Concat(Value('1/'), ExtractMonth('date_enrolled'), Value('/'), ExtractYear("date_enrolled"),
        #               output_field=CharField(), )

        if(format=="monthly"):
            return monthly
        elif format=="daily":
            return daily
        elif format== "yearly":
            return ExtractYear('date_enrolled')
        elif format=="gender":
            return Value("gender",output_field=CharField())
        elif format=="school":
            id=Cast("class_id__school_id",output_field=TextField())
            return Concat("class_id__school__school_name",Value(','),id,output_field=CharField())
        elif format=="stream":
            return Concat("class_id__class_name",Value(''),output_field=CharField())

        elif format=="county":
            return Concat("class_id__school__zone__subcounty__county__county_name",Value(''),output_field=CharField())
        elif format=="class":
            id=Cast("class_id", output_field=TextField())
            return Concat("class_id___class",Value(''),output_field=CharField())
        else:
            return monthly


def get_class(s):
    s=list(s)
    theclass=""
    for d in s:
        if d.isdigit():
            theclass=d
            break
    return str(theclass)

class ImportStudentSerializer(serializers.Serializer):
    fstname=serializers.CharField(max_length=50)
    midname=serializers.CharField(max_length=50,required=False,allow_null=True,allow_blank=True)
    lstname=serializers.CharField(max_length=50,required=False,allow_null=True,allow_blank=True)
    admission_no=serializers.CharField(max_length=50,required=False,allow_null=True,allow_blank=True)
    school=serializers.IntegerField()
    clas=serializers.CharField(max_length=50)
    gender=serializers.CharField(max_length=20)
    date_enrolled=serializers.DateField()
    #date_enrolled=serializers.DateField(required=False,allow_null=True)
    # emis_code=serializers.IntegerField(required=False,allow_null=True)
    def validate_gender(self,value):
        allowed_gender_values=['m','f','female','male']
        if value.lower() not in allowed_gender_values:
            raise serializers.ValidationError("Wrong gender format")
        return value

    def validate_clas(self,value):
        cl=get_class(value)
        if cl=="":
            raise serializers.ValidationError("Only students between class 1 and 8")
        return value

class NoStudentsList(APIException):
    status_code = 400
    default_detail = 'Provide a list of students to move.'
    default_code = 'bad_request'

class BulkMoveStudentSerializer(serializers.Serializer):
    students=serializers.ListField(child=serializers.IntegerField(required=True))
    class_id=serializers.IntegerField()

    def validate_students(self,value):
        if value is None:
            raise serializers.ValidationError("This field is required.")
        elif type(value) is not list:
            raise serializers.ValidationError("Provive a list of students.")
        return value

    def validate_class_id(self,value):
        if Stream.objects.filter(id=value).exists():
            return value
        raise serializers.ValidationError("Class does not exist")

class BulkMoveStudents(APIView):
    def post(self,request,format=None):
        ser=BulkMoveStudentSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        lis=ser.validated_data.get("students")
        if len(lis) == 0: raise NoStudentsList
        classid=ser.validated_data.get("class_id")
        print (lis,classid)
        lis=Students.objects.filter(id__in=lis).values_list("id",flat=True)
        f=Students.objects.filter(id__in=lis).update(class_id=classid)
        # hist = History()
        # hist.student = stud
        # hist._class = serializer.validated_data.get("class_id")
        # hist.joined = stud.date_enrolled
        # hist.joined_description = "Class Change"
        # hist.save()
        hist=[History(student_id=d,_class_id=classid,joined_description="Class Change") for d in lis]
        History.objects.bulk_create(hist)

        return Response({"updated":f},status=status.HTTP_202_ACCEPTED)




def next_class(s):
    s=s.split(' ')[1]
    if s=="ECD":
        return "Std 1"
    return "Std "+str(int(s)+1)

def get_stream(s):
    d=list(s)
    theclass=get_class(s)
    d.pop(d.index(theclass))
    return ''.join(d)

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

def create_user(username):
    users=User.objects.filter(username=username)
    if not users.exists():
        user = User.objects.create_user(username=username, password="admin")
        g,created = Group.objects.get_or_create(name="teachers")
        #print (g,created)
        g.user_set.add(user)
        return user
    return users[0]

class ImportStudents(APIView):
    permission_classes = (IsTeacherOrPartner,)
    def post(self,request,format=None):
        #File with students details
        file=request.FILES["file"]
        #Convert each row into array
        data = [row for row in csv.reader(file.read().splitlines())]
        d=""
        s=0
        rowindex=[]
        err=""
        the_data=data[1:]
        with transaction.atomic():
            thelen=len(the_data)
            for i,dat in enumerate(the_data):
                print (i)
                #print (str((float(i)/float(thelen))*100)+" %")
                dt={"fstname":dat[6],"midname":dat[7],"lstname":dat[8], "school":dat[5],
                    "clas":dat[13],"gender":dat[11]}
                ser=ImportStudentSerializer(data=dt)
                is_partner = Group.objects.get(name="partners").user_set.filter(id=request.user.id).exists()
                partner = None
                if is_partner:
                    partner = Partner.objects.filter(user=request.user)[0]
                school_name=dat[4]
                if ser.is_valid():
                    sch=Schools.objects.filter(emis_code=ser.data.get("school"))
                    teach=Teachers()
                    if(sch.exists()):
                        sch=sch[0]
                        if partner:
                            if not partner in sch.partners.all():
                                sch.partners.add(partner)
                        teach = Teachers.objects.filter(school=sch)
                        if(not teach.exists()):
                            #print ("No teacher")
                            user=create_user(sch.emis_code)
                            teacher=Teachers()
                            teacher.user=user
                            teacher.headteacher=True
                            teacher.active=True
                            teacher.fstname="Admin"
                            teacher.lstname=sch.school_name.split(' ')[0]
                            teacher.teacher_type="TSC"
                            teacher.gender="M"
                            teacher.school=sch
                            teacher.phone_no="99999999999"
                            teach =teacher.save()
                            #print (teach)
                            #return Response("Create atleast one Teacher for the school")
                        else:
                            teachs=teach.filter(headteacher=True)
                            if not teachs.exists():
                                teach=teach[0]
                            else:
                                teach=teachs[0]
                    else:
                        print ("Create "+school_name +" First")
                        continue
                        #return Response("Create School First")
                    nxt_class=ser.data.get("clas")
                    theclass=get_class(nxt_class)
                    ##Confirm a class has been entered
                    #print ("Class "+theclass)
                    if theclass is None:
                        continue
                    if not nxt_class == "Std 9":
                        cls=Stream.objects.filter(class_name=nxt_class,school=sch)
                        cl = Stream()
                        if not (cls.exists()):
                            cl.class_name=nxt_class
                            cl._class_id=theclass
                            cl.school=sch
                            cl.teacher=teach
                            cl=cl.save()
                        else:
                            cl = cls[0]
                        if(cl is None):
                            continue
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
                                lst = str(datetime.now().date() - timedelta(days=35))
                                if(std.date_enrolled>lst):
                                    std.is_oosc=True
                                else:
                                    std.is_oosc=False
                            else:
                                std.date_enrolled=datetime.now()
                                std.is_oosc=True
                            #print(std.class_id)
                            std.save()
                            s += 1

                    # else:
                    #     #print("Done Kcpe")
                else:

                    err=ser.errors
                    #print(err)
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

class AbsentStudentSerializer(serializers.Serializer):
    student_id=serializers.IntegerField(required=False)
    absent_count=serializers.IntegerField(required=False)
    name=serializers.CharField(required=False)
    school_name=serializers.CharField(required=False)
    class_name=serializers.CharField(required=False)
    class_id=serializers.IntegerField(required=False)
    guardian_phone=serializers.CharField(required=False)
    guardian_name=serializers.CharField(required=False)
    gender=serializers.CharField(required=False)
    present_count=serializers.IntegerField(required=False)


class ImportStudentsV2(APIView):
    total_success = 0
    total_fails = 0
    total_duplicates=0
    is_oosc=False

    def str2bool(self,v):
        return v.lower() in ("yes", "true", "t", "1")

    def post(self,request,format=None):
        file=""
        results=""
        verify=request.query_params.get('verify',None)
        isoosc=request.query_params.get('is_oosc',"no")
        self.is_oosc= self.str2bool(isoosc)
        print("the is_ooc",self.is_oosc)
        try:
            file = request.FILES["file"]
        except:
            return Response("No .csv file sent", status=status.HTTP_400_BAD_REQUEST)
        data=""
        # Convert each row into array and ignore the header row
        if file:
            data = [row for row in csv.reader(file.read().splitlines())][1:]

        if (verify):
            if verify=="update_oosc":
                results=self.update_oosc_status(data)
            else:
                results=self.verify_data(data)
        else:
            results=self.import_data(data,request)
        return Response(results)

    def update_oosc_status(self,data):
        total_success = 0
        total_fails = 0
        errors = []
        students=[]
        #print(len(data))
        for i ,dat in enumerate(data):
            stdout.write("\rImporting  %d" % i)
            stdout.flush()
            dt = {"fstname": dat[6], "midname": dat[7], "lstname": dat[8], "school": dat[5],
                  "admission_no":dat[9],
                  "clas": dat[13], "gender": dat[11],"date_enrolled":dat[2]}

            ser = ImportStudentSerializer(data=dt)
            if ser.is_valid():
                school = Schools.objects.filter(emis_code=ser.validated_data.get("school"))
                if school.exists():
                    school=school[0]
                    #print ("No school")
                else:
                    continue
                cl = self.get_class(school, ser.validated_data.get("clas"))
                if  cl is None:
                    #print ("No sclass")
                    continue
                std = Students.objects.filter(fstname=ser.data.get("fstname"), lstname=ser.data.get("lstname"),
                                              midname=ser.data.get("midname"),
                                              admission_no=ser.data.get("admission_no"),
                                              class_id=cl)
                if(std.exists()):
                    std=std[0]
                    students.append(std.id)
                    total_success+=1
                else:
                    #stdout.write("\r No student  ")
                    total_fails+=1
            else:
                total_fails+=1

        print ""
        total_success=Students.objects.filter(id__in=students).update(is_oosc=self.is_oosc)
        res = ImportResults(ImportErrorSerializer(errors, many=True).data, total_success, total_fails,0)
        return ImportResultsSerializer(res).data





    def verify_data(self,data):
        results="verified results"
        total_success=0
        total_fails=0
        errors=[]
        schools_not_created=[]
        total = len(data)
        with transaction.atomic():
            for i, dat in enumerate(data):
                if (total is not 0):
                    percentage=str(int(i / float(total) * 100))+"%"
                    stdout.write("\rVerifying %s " % percentage)
                    stdout.flush()
                dt = {"fstname": dat[6], "midname": dat[7], "lstname": dat[8], "school": dat[5],
                      "admission_no": dat[9],
                      "clas": dat[13], "gender": dat[11]}
                ser = ImportStudentSerializer(data=dt)
                if(ser.is_valid()):
                    ##Confirm the school in the db
                    school=Schools.objects.filter(emis_code=ser.validated_data.get("school"))
                    if(school):
                        total_success = total_success + 1
                    else:
                        total_fails += 1
                        error = ImportError(i + 2, "Create school first", json.dumps(dt))
                        # errors.append(error)
                        # continue
                        if ser.validated_data.get("school") not in schools_not_created:
                            errors.append(error)
                            schools_not_created.append(ser.validated_data.get("school"))
                        # if ser.validated_data.get("school") not in schools_not_created:
                        #     errors.append(error)
                        #     schools_not_created.append(ser.validated_data.get("school"))
                else:
                    total_fails=total_fails+1
                    #Adding 2 to row error due to header plus header is removed
                    error=ImportError(i+2,ser.errors,json.dumps(dt))
                    errors.append(error)
            #Print a new line
            #print("")
        res=ImportResults(ImportErrorSerializer(errors,many=True).data,total_success,total_fails,self.total_duplicates)
        return ImportResultsSerializer(res).data
    def import_data(self,data,request):
        results="Imported results"
        errors = []
        school=""
        schools_not_created = []
        students=[]
        total=len(data)
        is_partner = Group.objects.get(name="partners").user_set.filter(id=request.user.id).exists()
        partner = None
        if is_partner:
            partner = Partner.objects.filter(user=request.user)[0]

        print ("%d" %total)
        for i, dat in enumerate(data):
            if (total is not 0):
                percentage = str(int(i+1 / float(total) * 100)) + "%"
                stdout.write("\rImporting %s " % percentage)
                stdout.flush()
            dt = {"fstname": dat[6], "midname": dat[7], "lstname": dat[8], "school": dat[5],
                  "admission_no": dat[9],
                  "clas": dat[13], "gender": dat[11],"date_enrolled":dat[2]}
            ser = ImportStudentSerializer(data=dt)
            if (ser.is_valid()):
                ##Confirm the school in the db

                school = Schools.objects.filter(emis_code=ser.validated_data.get("school"))
                if (school.exists()):
                    try:
                        school=school[0]
                        if partner:
                            if not partner in school.partners.all():
                                school.partners.add(partner)
                        ##Confirm a teacher is present for login
                        teach =self.get_school_teacher(school)
                        clas=self.get_class(school,ser.validated_data.get("clas"))
                        student=self.create_student(clas,ser,dat[2])
                        if student is not None:
                            students.append(student)

                    except Exception as e:
                        self.total_fails += 1
                        error=ImportError(i + 2, e.message, json.dumps(dt))
                        errors.append(error)
                else:
                    self.total_fails += 1
                    error = ImportError(i + 2, "Create school first", json.dumps(dt))
                    #errors.append(error)
                    #continue
                    if ser.validated_data.get("school") not in schools_not_created:
                        errors.append(error)
                        schools_not_created.append(ser.validated_data.get("school"))
            else:
                self.total_fails += 1
                # Adding 2 to row error due to header plus header is removed
                error = ImportError(i + 2, ser.errors, json.dumps(dt))
                errors.append(error)
        try:
            resa = Students.objects.bulk_create(students)
            self.total_success=len(resa)
        except Exception as e:
            print (e.message)

        ##Updating the last upload data for partner
        if self.total_success >0:
            if partner:
                Partner.objects.filter(id=partner.id).update(last_data_upload=datetime.now())
        res = ImportResults(ImportErrorSerializer(errors, many=True).data, self.total_success , self.total_fails,self.total_duplicates)
        dt= ImportResultsSerializer(res).data
        print({"success":self.total_success,"duplicates":self.total_duplicates,"error":len(errors)})
        return dt

    def get_school_teacher(self,sch):
        teach=Teachers.objects.filter(school=sch)
        if (not teach.exists()):
            # print ("No teacher")
            user = create_user(sch.emis_code)
            teacher = Teachers()
            teacher.user = user
            teacher.headteacher = True
            teacher.active = True
            teacher.fstname = "Admin"
            teacher.lstname = sch.school_name.split(' ')[0]
            teacher.teacher_type = "TSC"
            teacher.gender = "M"
            teacher.non_delete=True
            teacher.school = sch
            teacher.phone_no = "99999999999"
            teach = teacher.save()
            # print (teach)
            # return Response("Create atleast one Teacher for the school")
        else:
            teachs = teach.filter(headteacher=True)
            if not teachs.exists():
                teach = teach[0]
            else:
                teach = teachs[0]
        return teach


    def get_class(self, school,clas):
        fullname,dd,dd=get_stream_name_regex(clas)
        cls = Stream.objects.filter(class_name__icontains=fullname, school=school)
        cl = Stream()
        if not (cls.exists()):
            cl.class_name = fullname
            cl._class_id =get_class(clas)
            cl.school = school
            cl.save()
        else:
            cl = cls[0]
        return cl

    def create_student(self, cl, ser,date_enrolled):
        std = Students.objects.filter(fstname=ser.data.get("fstname"), lstname=ser.data.get("lstname"),
                                      midname=ser.data.get("midname"),
                                      admission_no=ser.data.get("admission_no"),
                                      class_id=cl)
        # check if student Exists
        if (std.exists()):
            # print "Found"
            std=None
            self.total_duplicates += 1
        else:
            std = Students()
            std.fstname = ser.data.get("fstname")
            std.midname = ser.data.get("midname")
            std.lstname = ser.data.get("lstname")
            std.date_enrolled=ser.data.get("date_enrolled")
            std.gender = get_gender(ser.data.get("gender"))
            std.graduated=False
            std.is_oosc=self.is_oosc
            std.class_id = cl
            # if (valid_date(date_enrolled)):
            #     std.date_enrolled = date_enrolled
            #     lst = str(datetime.now().date() - timedelta(days=35))
            #     if (std.date_enrolled > lst):
            #         std.is_oosc = True
            #     else:
            #         std.is_oosc = False
            # else:
            #     std.date_enrolled = datetime.now()
            #     std.is_oosc = True
            #std.save()
            self.total_success += 1
        return std

class ListAbsentStudents(generics.ListAPIView):
    queryset=Attendance.objects.all()
    serializer_class = StudentsSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = AttendanceFilter

    def get_queryset(self):
        atts=Attendance.objects.all()
        atts=self.filter_queryset(atts)
        atts=atts.order_by('student').values("student_id")\
            .annotate(present_count=Count(Case(When(status=1,then=1),
            output_field=IntegerField())),
            name=Concat(F("student__fstname"),Value(' '),F("student__lstname")),
            school_name=F("student__class_id__school__school_name"),
            class_name=F("student__class_id__class_name"),
            class_id=F('student__class_id'),
            guardian_phone=F("student__guardian_phone"),
            guardian_name=F("student__guardian_name"),
            gender=F("student__gender"),
            absent_count=Count(Case(When(status=0,then=1),
            student_id='student',
            output_field=IntegerField())))
        atts = atts.exclude(absent_count=0).exclude(student_id__active=False)
        return atts

    def get_serializer_class(self):
        return AbsentStudentSerializer


class UpdateStudentsOoscStatus(generics.UpdateAPIView):
    queryset = Students.objects.all()
    serializer_class = StudentsUpdateOoscSerializer
    #lookup_field = "id"

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data.get("students"))
        records=Students.objects.filter(id__in=serializer.validated_data.get("students"))\
            .update(is_oosc=serializer.validated_data.get("is_oosc"))
        return Response({"detail":"Ok","detail_description":"{0} record updated.".format(records)})

    def get_object(self):
        pass


class GetDroupoutsWithReasons(generics.ListAPIView):
    queryset = Students.objects.filter(active=False,graduated=False)
    serializer_class=SimpleStudentSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class=StudentFilter

    # def list(self, request, *args, **kwargs):
    #     queryset = self.filter_queryset(self.get_queryset())
    #
    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         # serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(queryset)
    #     return Response(queryset)

    def get_queryset(self):
        hist=History.objects.filter(student_id=OuterRef('pk')).order_by("modified").values_list("left_description")
        # self.queryset.filter(is_oosc=True).annotate(logs=Subquery(hist[:1]),
        #                                             name=Concat(F("fstname"), Value(" "), F("midname"), Value(" "),
        #                                                         F("lstname"))).filter(logs="DROP").update("")
        return self.queryset.filter(is_oosc=True).annotate(logs=Subquery(hist[:1]),
                                      name=Concat(F("fstname"),Value(" "),F("midname"),Value(" "),F("lstname"))).filter(logs="DROP")


class ListDropouts(generics.ListAPIView):
    queryset = Students.objects.filter(active=False)
    serializer_class = StudentsSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = EnrollmentFilter

class ExportStudentsData(generics.ListAPIView):
    queryset = Students.objects.select_related("class_id", "class_id__school")
    serializers_class=StudentsSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = StudentFilter

    def list(self, request, *args, **kwargs):
        school = request.query_params.get("school", None)
        queryset=self.filter_queryset(self.queryset)
        queryset=queryset.exclude(active=False,class_id=None)
        queryset=queryset.annotate(class_name=F("class_id__class_name"),
                         school_name= F("class_id__school__school_name"),
                         school_emis_code=F("class_id__school__emis_code"),
                         )
        queryset=queryset.values("id","fstname","midname","lstname","gender","class_id","is_oosc","class_name","school_name","school_emis_code")
        queryset=queryset.order_by("school_emis_code","class_name")
        # print ("stuff")
        # print("have the queryset")
        queryset=list(queryset)
        path=excel_generate(queryset,include_days=False)
        # path = default_storage.save('exports/file.xlsx',wb)
        # print (default_storage(path).base_url)
        url = request.build_absolute_uri(location="/media/"+path)
        resp={"link":url}
        # print(resp)
        return  Response(resp)

class ExportStudents(generics.ListAPIView):
    queryset = Students.objects.select_related("class_id", "class_id__school")
    serializers_class=StudentsSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = StudentFilter

    def list(self, request, *args, **kwargs):
        school = request.query_params.get("school", None)
        start_date, end_date=self.parse_querparams()

        if school == None:
            raise MyCustomException("You can only generate for a certain school",400)
        queryset=self.filter_queryset(self.queryset)
        queryset=queryset.exclude(active=False,class_id=None)
        queryset=queryset.annotate(class_name=F("class_id__class_name"),
                         school_name= F("class_id__school__school_name"),
                         school_emis_code=F("class_id__school__emis_code"),
                         )
        queryset=queryset.values("id","fstname","midname","lstname","gender","class_id","class_name","school_name","school_emis_code")
        queryset=queryset.order_by("school_emis_code","class_name")
        # print ("stuff")
        # print("have the queryset")
        # filename="test"
        # queryset=[{"school_title":"Warugara","count":4}]
        # headers=[{"name":"School Title","value":"school_title"},{"name":"Students Count","value":"count"},{"name":"Test  Final","value":"test"}]
        # path=exportcsv(filename=filename,queryset=queryset,headers=headers,title="Schools")
        # print(path)
        # print("The path taken by the export")
        queryset=list(queryset)
        if len(queryset) == 0:
            raise MyCustomException("No Data found.",400)
        filename="Attendance_%s_%s"%(start_date,end_date)
        headers=[{"name":"School Name","value":"school_name"},{"name":"Emis Code","value":"school_emis_code"},{"name":"Student System Id","value":"id"},
                 {"name": "First Name", "value": "fstname"},{"name":"Mid Name","value":"midname"},{"name":"Last Name","value":"lstname"},{"name":"Gender","value":"gender"},
                 {"name": "System Class Id", "value": "class_id"},{"name":"Class Name","value":"class_name"}]

        thedays = get_list_of_dates(start_date=start_date, end_date=end_date)
        daysheaders=[{"name":str(d).split(" ")[0],"value":d} for d in thedays]
        allheaders=headers+daysheaders
        path = exportcsv(filename=filename, queryset=queryset, headers=allheaders, title="Attendance")
        # path=excel_generate(queryset)
        # path = default_storage.save('exports/file.xlsx',wb)
        # print (default_storage(path).base_url)
        url = request.build_absolute_uri(location="/media/"+path)
        resp={"link":url}
        # print(resp)
        return  Response(resp)

    def parse_querparams(self):
        start_date = self.request.GET.get("start_date", None)
        end_date = self.request.GET.get("end_date", None)
        if start_date == None or end_date == None: raise MyCustomException(
            "You must include the `start_date` , `end_date` ,  in the query params");
        return start_date, end_date