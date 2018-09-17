from django.db import transaction
from django.db.models import Case, CharField, F
from django.db.models import Count
from django.db.models import Q
from django.db.models import Value
from django.db.models import When
from django.db.models.functions import Concat
from django.shortcuts import render
from django_subquery.expressions import OuterRef, Subquery

from oosc.history.models import History
from oosc.schools.models import Schools
from rest_framework import generics
from oosc.schools.serializers import SchoolsSerializer, PostSchoolSerializer
from rest_framework import status
from rest_framework.response import Response
from oosc.counties.models import Counties
from oosc.subcounty.models import SubCounty
from oosc.teachers.views import str2bool
from oosc.zone.models import Zone
from oosc.teachers.models import Teachers
from oosc.students.models import Students
from django.http import Http404
from django_filters.rest_framework import FilterSet,DjangoFilterBackend
import django_filters
from django.contrib.auth.models import Group


from django.conf import settings
import csv,codecs
from rest_framework.permissions import IsAdminUser
# Create your views here.
from rest_framework.views import APIView
from django.core.files.storage import FileSystemStorage
import time
from rest_framework.pagination import PageNumberPagination

from oosc.partner.models import Partner
from oosc.schools.permissions import IsPartner


class SchoolsFilter(FilterSet):
    county=django_filters.NumberFilter(name="county_filter",method="filter_county",label="County Id")
    school_name=django_filters.CharFilter(name='school_name',label="School Name",lookup_expr="icontains")
    partner=django_filters.NumberFilter(name="partner" ,label="Partner Id" ,method="filter_partner")
    partner_conflict=django_filters.CharFilter(name="partner_conflict" ,label="Partner Conflict (true,false)" ,method="filter_partner_conflict")
    active=django_filters.BooleanFilter(name="active" ,label="Active (1=True,2=False)" ,method="filter_active")
    partner_admin=django_filters.NumberFilter(name="active" ,label="Partner Admin" ,method="filter_partner_admin")
    class Meta:
        model=Schools
        fields=('id','emis_code','zone','county',"school_name",'partner','partner_conflict')

    def filter_county(self,queryset,name,value):
        return queryset.exclude(Q(zone=None) | Q(subcounty=None)).filter(Q(zone__subcounty__county=value) | Q(subcounty__county=value))


    def filter_partner(self,queryset,name,value):
        return queryset.filter(partners__id=value)

    def filter_partner_conflict(self,queryset,name,value):
        value=str2bool(value)
        return queryset.filter(partner_conflict=value)

    def filter_partner_admin(self,queryset,name,value):
        return  queryset.filter(partners__partner_admins__id=value)

    def filter_active(self, queryset, name, value):
        return queryset.filter(stream__isnull=False).distinct()

class StandardresultPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 1000
    page_size_query_param = 'page_size'

class ListCreateSchool(generics.ListCreateAPIView):
    queryset=Schools.objects.select_related().prefetch_related("partners")
    serializer_class=SchoolsSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class=SchoolsFilter
    pagination_class = StandardresultPagination
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
def convert_to_emis_code_number(emis_code):
    emis=''.join(c for c in emis_code if c.isdigit())
    ##print (emis)
    return emis

class ImportSchools(APIView):
    permission_classes = (IsPartner,)
    thezone=Zone()
    def post(self,request,format=None):
        file=request.FILES["file"]
        data = [row for row in csv.reader(file.read().splitlines())]
        print (data)
        start=time.time()
        schools=[]

        with transaction.atomic():
            for indx,d in enumerate(data):
                #print (indx,len(data))
                emis = convert_to_emis_code_number(d[1])
                if not emis.isdigit():
                    continue
                emis=int(emis)
                is_partner = Group.objects.get(name="partners").user_set.filter(id=request.user.id).exists()
                partner=None
                if is_partner:
                    partner=Partner.objects.filter(user=request.user)[0]
                if(indx>=0):
                    ##Check if county present
                    if self.thezone.name!=d[4]:
                        coun=Counties.objects.filter(county_name__contains=d[2])
                        cn = Counties()
                        if(len(coun)>0):
                            ##print (coun[0].county_name)
                            cn=coun[0]
                        else:
                            cn.county_name=d[2]
                            cn.save()
                        #Check if subcounty present in db
                        sub=SubCounty.objects.filter(name__contains=d[3])
                        su = SubCounty()
                        if(len(sub)>0):
                            ##print (sub[0].name)
                            su=sub[0]
                        else:
                            su.county=cn
                            su.name=d[3]
                            su.save()
                        #check if zone present in db
                        zones=Zone.objects.filter(name__contains=d[4])
                        zone = Zone()
                        if(len(zones)>0):
                            ##print (zones[0].name)
                            zone=zones[0]
                        else:

                            zone.county=cn
                            zone.subcounty=su
                            zone.name=d[4]
                            zone.save()
                        self.thezone=zone
                    else:
                        zone=self.thezone
                    #Schools
                    schs=Schools.objects.filter(emis_code=emis)
                    sch = Schools()
                    if(len(schs)>0):
                        #print (schs[0].school_name)
                        sch = schs[0]
                    else:
                        sch.school_name=d[5]
                        sch.zone=zone
                        sch.level=d[6].upper()
                        sch.status=d[7].upper()
                        sch.emis_code=emis
                        schools.append(sch)
                        # sch.save()
                        # if partner:
                        #     sch.partners.add(partner)
        sc=[]
        sc=Schools.objects.bulk_create(schools)
        print(time.time()-start,len(sc))
        return Response(data=data[1])

class SearchEmiscode(generics.RetrieveUpdateAPIView):
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
        schools = Schools.objects.all()
        activeschools=schools.filter(streams__isnull=False)
        teachers = Teachers.objects.all()
        partner=request.query_params.get("partner",None)
        partner_admin=request.query_params.get("partner_admin",None)

        if partner:
            students=students.filter(class_id__school__partners__id=partner)
            teachers=teachers.filter(school__partners__id=partner)
            schools=schools.filter(partners__id=partner)
            activeschools=activeschools.filter(partners__id=partner)
        if partner_admin:
            students = students.filter(class_id__school__partners__partner_admins__id=partner_admin)
            teachers = teachers.filter(school__partners__partner_admins__id=partner_admin)
            schools = schools.filter(partners__partner_admins__id=partner_admin)
            activeschools = activeschools.filter(partners__partner_admins__id=partner_admin)

        sts = list(students.order_by().annotate(type=Case(
            When(Q(is_oosc=False) & Q(gender="F") & Q(active=False), then=Value("dropout_old_females")),
            When(Q(is_oosc=False) & Q(gender="M") & Q(active=False), then=Value("dropout_old_males")),
            When(Q(is_oosc=False) & Q(gender="M") & Q(active=False), then=Value("dropout_old_males")),
            When((Q(is_oosc=True) & Q(gender="M") & Q(active=False)), then=Value("dropout_enrolled_males")),
            When(Q(is_oosc=True) & Q(active=False) & Q(gender="F"), then=Value("dropout_enrolled_females")),
            When(Q(is_oosc=True) & Q(gender="M") & Q(active=True), then=Value("enrolled_males")),
            When(Q(is_oosc=True) & Q(gender="F") & Q(active=True), then=Value("enrolled_females")),
            When(Q(is_oosc=False) & Q(gender="F") & Q(active=True), then=Value("old_females")),
            When(Q(is_oosc=False) & Q(gender="M") & Q(active=True), then=Value("old_males")),
            default=Value("others"),
            output_field=CharField()
        )).values("type").annotate(count=Count("type")))
        mstudents=self.get_count(sts,"old_males") + self.get_count(sts,"enrolled_males") #students.filter(gender="M").count()
        fstudents=self.get_count(sts,"old_females") + self.get_count(sts,"enrolled_females")#students.filter(gender="F").count()
        mdropouts=self.get_count(sts,"dropout_old_males") + self.get_count(sts,"dropout_enrolled_males") #students.filter(gender="M").count()
        fdropouts=self.get_count(sts,"dropout_old_females") + self.get_count(sts,"dropout_enrolled_females")#students.filter(gender="F").count()

        hist = History.objects.filter(student_id=OuterRef('pk')).order_by("modified").values_list("left_description")
        totals=Students.objects.filter(is_oosc=True).annotate(logs=Subquery(hist[:1]),
                                                           name=Concat(F("fstname"), Value(" "), F("midname"),
                                                                       Value(" "), F("lstname"))).filter(logs="DROP").count()

        # oldmstudents=students.filter(gender="M",is_oosc=False,active=True).count()
        # newmstudents=students.filter(gender="M",is_oosc=True,active=True).count()
        # dropoldmstudents=students.filter(gender="M",is_oosc=False,active=False).count()
        # dropnewmstudents=students.filter(gender="M",is_oosc=True,active=False).count()
        # newfstudents=students.filter(gender="F",is_oosc=True,active=True).count()
        # oldfstudents=students.filter(gender="F",is_oosc=False,active=True).count()
        # dropoldfstudents=students.filter(gender="F",is_oosc=False,active=False).count()
        # dropnewftudents=students.filter(gender="F",is_oosc=True,active=False).count()

        activeschools=activeschools.distinct().count()
        teachers=teachers.count()
        schools=schools.count()

        return Response(data={"schools":schools,"active_schools":activeschools,
                              "teachers":teachers,
                              "students":{"males":mstudents,
                                          "females":fstudents,
                                          "dropout_males":totals,
                                          "dropout_females":0
                                          }})

    def get_count(self, list, item):
        obs = [g["count"] for g in list if g["type"] == item]
        if len(obs) > 0: return obs[0]
        return 0

