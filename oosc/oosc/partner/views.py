import csv
import time
from django.shortcuts import render
from django_subquery.expressions import Subquery, OuterRef
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView

from oosc.mylib.common import MyCustomException
from oosc.partner.models import Partner
# Create your views here.
from rest_framework import generics,status
from django.contrib.auth.models import User, Group
from oosc.partner.serializers import PartnerSerializer, PostPartnerSerializer, SavePartnerSerializer, \
    PartnerAdminSerializer, PostPartnerAdminSerializer, SavePartnerAdminSerializer
from oosc.partner.permissions import IsAdmin
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from django_filters.rest_framework import FilterSet,DjangoFilterBackend
import django_filters
from django.db.models import Q
from django.db.models import Count,Case,When,IntegerField,Q,Value,CharField,Sum,Avg

from oosc.schools.models import Schools
from oosc.schools.serializers import SchoolsSerializer
from oosc.students.models import Students
from oosc.teachers.views import str2bool


class NameDuplicationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = u'User already exist'

class PartnerFilter(FilterSet):
    name=django_filters.CharFilter(name="name",lookup_expr="icontains")
    partner_admin=django_filters.CharFilter(name="name",label="Partner Admin",method="filter_partner_admin")
    class Meta:
        model=Partner
        fields=['name',"partner_admin"]

    def filter_partner_admin(self, queryset, name, value):
        return queryset.filter(partner_admins__id=value)


class StandardresultPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 1000
    page_size_query_param = 'page_size'

class PartnerSaveFail(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = u'Error creating partner'

class PartnerAdminSaveFail(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = u'Error creating partner admin'

class ListCreatePartner(generics.ListCreateAPIView):
    queryset = Partner.objects.select_related("user")
    serializer_class = PartnerSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (DjangoFilterBackend,)
    filter_class=PartnerFilter
    pagination_class = StandardresultPagination

    # def get_queryset(self):
    #     f = Count(Case(When(Q(gender="F"), then=1), output_field=IntegerField(), ))
    #     m = Count(Case(When(Q(gender="M"), then=1), output_field=IntegerField(), ))
    #     pt=Students.objects.filter(is_oosc=True,active=True,class_id__school__partners__id=OuterRef('id')).select_related("user").order_by().values("is_oosc").annotate(males=m,females=f,total=Count("is_oosc"))
    #     males = Subquery(pt.values("males")[:1], output_field=IntegerField())
    #     total = Subquery(pt.values("total")[:1], output_field=IntegerField())
    #     females = Subquery(pt.values("females")[:1], output_field=IntegerField())
    #     return Partner.objects.annotate(total=total,females=females,males=males)



    def get_serializer_class(self):
        if self.request.method == "POST":
            return PostPartnerSerializer
        else:
            return PartnerSerializer

    def get_queryset(self):
        all = str2bool(self.request.query_params.get('all', False))
        # print (all)
        if  all:
            return Partner.objects.all()
        return  Partner.objects.filter(test=False)


    def perform_create(self, serializer):
        username=serializer.validated_data.get("email")
        password="#partner"
        name=serializer.validated_data.get("name")
        user=""
        try:
            user=User.objects.create_user(username=username,
                                      email=username,password=password)
        except Exception as e:
            print (e.message)
            raise NameDuplicationError
        g, created = Group.objects.get_or_create(name="partners")
        # print (g,created)
        g.user_set.add(user)
        data=serializer.data
        data["user"]=user.id
        partner=SavePartnerSerializer(data=data)
        if not partner.is_valid():
            raise serializer.ValidationError(str(partner.errors))
        else:
            #
            try:
                partner.save()
            except Exception as e:
                #print (e.message,partner.validated_data)
                user.delete()
                raise PartnerSaveFail


class ListCreatePartnerAdmin(generics.ListCreateAPIView):
    queryset = Partner.objects.select_related("user")
    serializer_class = PartnerAdminSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (DjangoFilterBackend,)
    filter_class=PartnerFilter
    pagination_class = StandardresultPagination

    # def get_queryset(self):
    #     f = Count(Case(When(Q(gender="F"), then=1), output_field=IntegerField(), ))
    #     m = Count(Case(When(Q(gender="M"), then=1), output_field=IntegerField(), ))
    #     pt=Students.objects.filter(is_oosc=True,active=True,class_id__school__partners__id=OuterRef('id')).select_related("user").order_by().values("is_oosc").annotate(males=m,females=f,total=Count("is_oosc"))
    #     males = Subquery(pt.values("males")[:1], output_field=IntegerField())
    #     total = Subquery(pt.values("total")[:1], output_field=IntegerField())
    #     females = Subquery(pt.values("females")[:1], output_field=IntegerField())
    #     return Partner.objects.annotate(total=total,females=females,males=males)
    def get_serializer_class(self):
        if self.request.method == "POST":
            return PostPartnerAdminSerializer
        else:
            return PartnerAdminSerializer

    def get_queryset(self):
        all = str2bool(self.request.query_params.get('all', False))
        # print (all)
        if  all:
            return Partner.objects.all()
        return  Partner.objects.filter(test=False)


    def perform_create(self, serializer):
        username=serializer.validated_data.get("email")
        password="#partneradmin"
        name=serializer.validated_data.get("name")
        user=""
        try:
            user=User.objects.create_user(username=username,
                                      email=username,password=password)
        except Exception as e:
            print (e.message)
            raise NameDuplicationError
        g, created = Group.objects.get_or_create(name="partner_admins")
        # print (g,created)
        g.user_set.add(user)
        data=serializer.data
        data["user"]=user.id
        partner=SavePartnerAdminSerializer(data=data)
        if not partner.is_valid():
            raise serializer.ValidationError(str(partner.errors))
        else:
            #
            try:
                partner.save()
            except Exception as e:
                #print (e.message,partner.validated_data)
                user.delete()
                raise PartnerAdminSaveFail

class RetrieveUpdateDestroyPartner(generics.RetrieveUpdateDestroyAPIView):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    permission_classes = (IsAdmin,)


class ClearPartnerSchools(APIView):
    def get(self,request,format=None):
        partners=list(Partner.objects.all())
        for partner in partners:
            print("")
            partner.schools.clear()
        ####Cleared allschools partners
        return  Response({"detail":"Reset all partner schools."})


# class
class AssignPartnerSchools(APIView):
    csv_headers=["school_name","school_emis_code"]
    def post(self,request,format=None):
        partner_id = self.request.data.get("partner", None)
        partner=self.validate_partner(partner_id)
        raw_emis_codes,data=self.get_parsed_data()
        print (data)
        ##Get all valid schools
        emis_codes=Schools.objects.filter(emis_code__in=raw_emis_codes).values_list("emis_code",flat=True)
        start = time.time()
        schools = []
        conflict_schools_emis_codes=Schools.objects.exclude(partners__id=partner_id).filter(emis_code__in=emis_codes).annotate(partners_count=Count("partners"))\
            .filter(partners_count__gte=1).values_list("emis_code",flat=True)
        ###Update conflict available
        Schools.objects.filter(emis_code__in=conflict_schools_emis_codes).update(partner_conflict=True)

        valid_codes=[d for d in emis_codes if d not in conflict_schools_emis_codes]
        valid_schools=Schools.objects.filter(emis_code__in=valid_codes)
        partner.schools.add(*valid_schools)
        # ser=SchoolsSerializer(partner.schools.all(),many=True)
        ser=partner.schools.count()
        # return Response({ "partner":partner_id, "detail":data,"emis_codes":emis_codes,"raw_emis_codes":conflict_schools_emis_codes,"res":ser})
        return Response({"detail":"Success","schools_count":ser,"partner_name":partner.name})


    def get_parsed_data(self):
        file = self.request.FILES.get("file", None)

        if not file:
            raise MyCustomException("File field required.")
        ###iGnore the header file
        data = [row for i,row in enumerate(csv.reader(file.read().splitlines())) if i !=0]
        return self.serialize_data(data)

    def validate_partner(self,partner):
        if not partner:
            raise MyCustomException("Field partner required.")
        partners=list(Partner.objects.filter(id=partner))
        if len(partners) == 0:
            raise MyCustomException("Partner not found.",404)
        return partners[0]


    def serialize_data(self,data):
        emis_codes=[]
        serialized_data=[]
        for value in data:
            c={self.csv_headers[i]:v for i,v in  enumerate(value)}
            emis_codes.append(value[1])
            serialized_data.append(c)
        return emis_codes,serialized_data





