from django.shortcuts import render

# Create your views here.

from rest_framework import generics
from rest_framework import serializers
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from oosc.mylib.common import MyCustomException, MyDjangoFilterBackend, StandardresultPagination
from oosc.promotions.models import PromoteSchool, PromoteStream
from oosc.promotions.serializers import PromoteSchoolSerializer
from oosc.stream.models import GraduatesStream
from django.db.models import F, Count, DateField, DateTimeField, CharField, IntegerField, Q
from django.db.models import Value
from django.db.models.functions import Concat
from django.db.models.functions import ExtractHour
from django.db.models.functions import ExtractMonth
from django.db.models.functions import ExtractYear
from django.db.models.functions import TruncDate
from django_filters.rest_framework import FilterSet,DjangoFilterBackend
import django_filters
from oosc.students.models import Students


class CreateListPromoteSchool(generics.ListCreateAPIView):
    queryset = PromoteSchool.objects.all()
    serializer_class =PromoteSchoolSerializer
    filter_backends = (MyDjangoFilterBackend,)

    def get_serializer_class(self):
        # GraduatesStream.objects.all().delete()
        return PromoteSchoolSerializer


class RetrievePromoteSschool(generics.RetrieveUpdateAPIView):
    queryset = PromoteSchool.objects.all()
    serializer_class =PromoteSchoolSerializer

class CompletePromotionSerializer(serializers.Serializer):
    action=serializers.CharField(max_length=20)

class RetrieveCompletePromoteSschool(generics.CreateAPIView):
    queryset = PromoteSchool.objects.all()
    serializer_class =CompletePromotionSerializer

    def create(self, request, *args, **kwargs):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )
        ##Clue id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        id = {self.lookup_field: self.kwargs[lookup_url_kwarg]}["pk"]
        self.validate_promotion_id(id)
        promotion=PromoteSchool.objects.get(id=id)
        action=serializer.validated_data.get("action").lower()
        if action=="complete":
            if promotion.completed:
                raise MyCustomException("Already completed promotions", 400)
            promotion.complete()
        elif action=="undo":
            if not promotion.completed:
                raise MyCustomException("Undo is only for completed promotions", 400)
            promotion.undo()
        return Response(PromoteSchoolSerializer(promotion).data)

    def validate_promotion_id(self,id):
        if not PromoteSchool.objects.filter(id=id).exists():
            raise MyCustomException("Promotion Config does not exist",404)


class PromoteSchoolFilter(FilterSet):
    school_emis_code=django_filters.NumberFilter(name="school__emis_code", label="School emis code")
    partner=django_filters.NumberFilter(name="",label="Partner  Id",method="filter_partner")
    partner_admin=django_filters.NumberFilter(name="",label="Partner Admin Id",method="filter_partner_admin")
    county=django_filters.NumberFilter(name="school__zone__subcounty__county",label="County Id")


    class Meta:
        model=PromoteSchool
        fields=('__all__')



    def filter_partner_admin(self,queryset,name,value):
        return  queryset.filter(school__partners__partner_admins__id=value)

    def filter_partner(self, queryset, name, value):
        return queryset.filter(school__partners__id=value)



class PromotionsStaisticsView(generics.ListCreateAPIView):
    queryset = PromoteSchool.objects.all()
    serializer_class = PromoteSchoolSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class=PromoteSchoolFilter

    formats = ["daily", "hourly", "monthly", "yearly", "radio", "device", "song", "country"]
    append_county_names = ["radio", "country"]
    format = None
    order_by = None
    pagination_class = StandardresultPagination

    def list(self, request, *args, **kwargs):
        self.order_by = self.request.query_params.get("order_by", None)
        queryset=""
        years=["2016","2017","2018","2019"]

        stds=[]
        querysett= self.filter_queryset(self.get_queryset())
        for year in years:
            pids= querysett.filter(completed=True,year=year).values_list("id",flat=True)
            stream_ids=PromoteStream.objects.filter(promote_school_id__in=pids,completed=True).values_list("next_class",flat=True)
            dts=Students.objects.filter(class_id__in=stream_ids).values("gender","is_oosc").annotate(count=Count("gender"))

            stds.append({
                "year":year,
                "data":dts
            })


        return Response(stds)


