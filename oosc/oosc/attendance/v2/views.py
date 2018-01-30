from django.db.models import Case
from django.db.models import F, Count,IntegerField
from django.db.models import Value
from django.db.models import When
from django.db.models.functions import Concat
from rest_framework import generics
from rest_framework.filters import DjangoFilterBackend
from rest_framework.response import Response

from oosc.attendance.models import Attendance
from oosc.attendance.serializers import AttendanceSerializer
from oosc.attendance.v2.serializers import ExportAttendanceSerializer
from oosc.attendance.views import AttendanceFilter
from oosc.mylib.common import MyCustomException
import calendar

from oosc.mylib.excel_export import export_attendance


class ExportMonthlyAttendances(generics.ListAPIView):
    queryset = Attendance.objects.select_related("_class", "_class__school")
    serializer_class=ExportAttendanceSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = AttendanceFilter
    monthyear=None


    def list(self, request, *args, **kwargs):
        # school = request.query_params.get("school", None)
        # if school == None:
        #     raise MyCustomException("You can only generate for a certain school",400)
        # queryset=self.filter_queryset(self.queryset)
        # queryset=queryset.exclude(active=False,class_id=None)
        # queryset=queryset.annotate(class_name=F("class_id__class_name"),
        #                  school_name= F("class_id__school__school_name"),
        #                  school_emis_code=F("class_id__school__emis_code"),
        #                  )
        # queryset=queryset.values("id","fstname","midname","lstname","class_id","class_name","school_name","school_emis_code")
        # queryset=queryset.order_by("school_emis_code","class_name")
        # print ("stuff")
        # print("have the queryset")
        # queryset=list(queryset)
        # path=excel_generate(queryset)
        # path = default_storage.save('exports/file.xlsx',wb)
        # print (default_storage(path).base_url)

        # url = request.build_absolute_uri(location="/media/"+path)
        # resp={"link":url}
        # print(resp)

        #####Parse the key:list from query_params to just a simple key:value pair

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

