import csv
from datetime import datetime

import sys
from django.db.models import Case
from django.db.models import F, Count,IntegerField
from django.db.models import Value
from django.db.models import When
from django.db.models.functions import Concat
from rest_framework import generics, status
from rest_framework.filters import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.views import APIView

from oosc.attendance.models import Attendance
from oosc.attendance.serializers import AttendanceSerializer
from oosc.attendance.v2.serializers import ExportAttendanceSerializer, \
    AttendanceImportErrorSerializer, AttendanceImportResultsSerializer
from oosc.attendance.views import AttendanceFilter
from oosc.mylib.common import MyCustomException, is_date
import calendar

from oosc.mylib.excel_export import export_attendance
from oosc.schools.models import Schools
from oosc.schools.views import ListCreateSchool
from oosc.stream.models import Stream
from oosc.stream.serializers import StreamSerializer
from oosc.stream.views import ListCreateClass, StreamFilter
from oosc.students.models import Students, ImportResults
from oosc.students.serializers import ImportResultsSerializer


class ExportMonthlyAttendances(generics.ListAPIView):
    queryset = Attendance.objects.select_related("_class", "_class__school")
    serializer_class=ExportAttendanceSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = AttendanceFilter
    monthyear=None

    def list(self, request, *args, **kwargs):
        # data={k[0]: k[1] for k in request.query_params.items()}
        print(self.parse_query_params())
        serializer=self.get_serializer(data=self.parse_query_params())
        serializer.is_valid(raise_exception=True)
        dd=self.get_queryset()
        if dd.count() ==0:
            raise MyCustomException("No attendance to export.",404)
        link=export_attendance(dd,**self.monthyear)
        url = request.build_absolute_uri(location="/media/" + link)
        resp = {"link": url}
        return  Response(resp)

    def get_queryset(self):
        queryset= self.filter_queryset(self.queryset)
        monthrange=calendar.monthrange(**self.monthyear)[1]
        # first_day=
        # print (monthrange)
        queryset=queryset.values("student").annotate(
            present=Count(Case(When(status=1,then=1),output_field=IntegerField())),
            absent=Count(Case(When(status=0,then=2),output_field=IntegerField())),
            total_attendance_days=Count("student"),
                    county_name= F("_class__school__zone__subcounty__county__county_name"),
                    subcounty_name= F("_class__school__zone__subcounty__name"),
                    total_month_days=Value(monthrange,output_field=IntegerField()),
                    school_name=F("_class__school__school_name"),
                    school_type=F("_class__school__status"),
                    school_emis_code=F("_class__school__emis_code"),
                    class_name=Concat(F('_class___class'),Value(" "),F("_class__class_name")) ,
                    gender=F("student__gender"),
                    guardian_name=F("student__guardian_name"),
                    guardian_phone=F("student__guardian_phone"),
                    dob_date=F('student__date_of_birth'),
                   student_name= Concat(F('student__fstname'),Value(" "),F("student__lstname")) )\
            .values("student","total_month_days","school_type","dob_date","county_name","school_type","subcounty_name","total_attendance_days","absent","present","student_name","school_name","guardian_name","guardian_phone","school_emis_code","class_name","gender")
        return queryset.order_by( "_class__school", "_class___class")




    def parse_query_params(self):
        ##convert into an array
        dd = self.request.query_params.items()
        # for d in dd:
        data = {k[0]: int(k[1]) if k[1].isdigit() else k[1] for k in dd}
        my=["month","year"]
        self.monthyear={k[0]: int(k[1]) if k[1].isdigit() else k[1] for k in dd if k[0] in my }
        print (self.monthyear)
        return data





class MonitorAttendanceTaking(generics.ListAPIView):
    serializer_class = AttendanceSerializer
    queryset = Stream.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_class=StreamFilter

    def get_queryset(self):
        self.queryset = self.filter_queryset(self.queryset)
        # self.get_schools()
        # print ("The attendances are ",self.queryset.count())

        return self.queryset

    def get_schools(self):
        filters=["county","partner"]
        attendance_streams=list(self.queryset().annotate(school=F("_class__school_id")).values("school")\
            .annotate(times=Count("school"))\
            .values_list("_class",flat=True))
        # print( "Attendance streams ", attendance_streams)

        classes_queryset=list(DjangoFilterBackend().filter_queryset(self.request,Attendance.objects.all(),ExportMonthlyAttendances))
        # no_attendances_streams = [d._class for d in classes_queryset if d._class not in attendance_streams ]
        # schools_queryset=DjangoFilterBackend().fi(self.request,Schools.objects.all(),self)
        # print( "The Streams are", classes_queryset.count())
        return classes_queryset

class AttendanceImportError:
    def __init__(self,row_number,error_message):
        self.row_number=row_number
        self.error_message=error_message

class ImportAttendance(APIView):
    myheaders=[]
    days_begin_index = 9
    success=0
    errors=[]
    duplicates=0
    records_success=0
    records_failed=0
    failed=0
    def post(self,request,format=None):
        self.myheaders = []
        self.success = 0
        self.errors = []
        self.duplicates = 0
        self.records_success = 0
        self.records_failed = 0
        self.failed = 0
        try:
            file = request.FILES["file"]
        except:
            raise MyCustomException("No .csv file sent")
        data = []
        # Convert each row into array and ignore the header row
        if file:
            try:
                data = [row for row in csv.reader(file.read().splitlines())]
            except Exception as e:
                print(e.message)
                raise MyCustomException("Error reading file. Make sure its a comma separated csv. {}".format(e.message))
        res=self.import_attendance(data)
        return Response(res)

    def import_attendance(self,rows):
        # now = str(datetime.now()).split(" ").pop(0).replace('-', '')#2018-07-0909 T767
        ##studen_id=index 2,class_id=index 7
        ##headers 8 collums
        self.myheaders=rows.pop(0)
        attendances=[]
        for i,row in enumerate(rows):
            sys.stdout.write("\rImporting... {}".format(i+1))
            attendances+=self.generate_attendance_for_row_each_student(i,row)
            if len(attendances) > 6000:
                self.bulk_create_attendances(attendances)
                attendances=[]
                # bulk_insert
        ###Do insert of remaining
        self.bulk_create_attendances(attendances)

        ###return response
        res = ImportResults(AttendanceImportErrorSerializer(self.errors, many=True).data, self.success, self.failed,self.duplicates)
        return AttendanceImportResultsSerializer(res).data

    def bulk_create_attendances(self,attendances):
        ## check the aattendaces that exists
        ids=[at.id for at in attendances]

        ###Filter the duplicate ids
        duplicates=Attendance.objects.filter(id__in=ids).values_list("id",flat=True)
        new=[]
        updates=[]
        for att in attendances:
            if att.id not in duplicates:
                new.append(att)
            else:
                updates.append(att)
        try:
            resa = Attendance.objects.bulk_create(new)
            self.success+=len(resa)
        except Exception as e:
            self.failed += len(attendances)
            print (e.message)

        ####Update the present ones
        ups=0
        for att in updates:
            try:
                att.save()
                ups+=1
            except Exception as e:
                print(e.message)
        self.duplicates+=ups

        print(self.success,self.failed,self.duplicates)



    def generate_attendance_for_row_each_student(self,index,rec):
        stud_id=rec[2]
        class_id=rec[7]
        days=rec[self.days_begin_index:]
        attendances=[]

        ##Validate class_id and_student_id
        has_student_id, has_class_id=self.validate_classid_sutdent_id(stud_id,class_id)
        if not has_class_id or not has_student_id:
            self.failed+=len(days)
            mess=[]
            if not has_student_id:mess.append("System Student Id")
            if not has_class_id:mess.append("System Class Id")
            self.errors.append(AttendanceImportError(row_number=index+2,error_message="Invalid {}".format("".join(mess))))
            return []

        for i,att in enumerate(days):
            thedate=self.get_row_date(i)
            if not is_date(thedate):
                erro_message="Wrong format date '{}'  in collumn {}. Accepted date format is YYYY-MM-DD.".format(thedate,i+1+self.days_begin_index)
                er=filter(lambda x:x.error_message==erro_message,self.errors)
                if len(er)<1:
                    self.errors.append(AttendanceImportError(row_number=0,error_message=erro_message))
                self.failed+=1
                continue
            attendance=Attendance(date=thedate,
                                  id="{}{}".format(thedate.replace("-",""),stud_id),
                                  status=self.parse_present_absent(att),
                                  _class_id=class_id,
                                  student_id=stud_id
                                  )
            attendances.append(attendance)
        return attendances



    def validate_classid_sutdent_id(self,student_id,class_id):
        has_student_id=Students.objects.filter(id=student_id).exists()
        has_class_id=Stream.objects.filter(id=class_id).exists()
        return has_student_id,has_class_id

    def get_row_date(self,index):
        try:
            return self.myheaders[index+self.days_begin_index]
        except:
            return ""

    def parse_present_absent(self,value):
        try:
            status=int(value)
            if(status==0):return 0
            elif status==1:return 1
            else:return 0
        except:
            return 0




