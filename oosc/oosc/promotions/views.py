from django.shortcuts import render

# Create your views here.

from rest_framework import generics
from rest_framework import serializers
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from oosc.mylib.common import MyCustomException, MyDjangoFilterBackend, StandardresultPagination
from oosc.promotions.models import PromoteSchool
from oosc.promotions.serializers import PromoteSchoolSerializer
from oosc.stream.models import GraduatesStream
from django.db.models import F, Count, DateField, DateTimeField, CharField, IntegerField
from django.db.models import Value
from django.db.models.functions import Concat
from django.db.models.functions import ExtractHour
from django.db.models.functions import ExtractMonth
from django.db.models.functions import ExtractYear
from django.db.models.functions import TruncDate

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


class PromotionsStaisticsView(generics.ListCreateAPIView):
    queryset = PromoteSchool.objects.all()
    serializer_class = PromoteSchoolSerializer
    filter_backends = (MyDjangoFilterBackend,)

    formats = ["daily", "hourly", "monthly", "yearly", "radio", "device", "song", "country"]
    append_county_names = ["radio", "country"]
    format = None
    order_by = None
    pagination_class = StandardresultPagination

    def list(self, request, *args, **kwargs):
        self.order_by = self.request.query_params.get("order_by", None)
        # print ("getting the stuff")
        queryset = self.get_queryset()
        # print (queryset)
        queryset = self.get_formatted_response_data(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            # serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(page)

        # serializer = self.get_serializer(queryset, many=True)

        return Response(queryset)



    def get_queryset(self):
        ##Get the class intent and set the
        self.queryset = self.filter_queryset(self.queryset)
        self.get_statistics_format()
        return self.get_formatted_date()

    def get_formatted_date(self):
        att= self.queryset.annotate(value=self.get_group_by()). \
            values("value")
        att=self.get_response_fields(att)

        return self.my_order_by(att)



    def my_order_by(self,queryset):
        # print("order...")
        # rev=self.request.query_params.get("order","DESC")
        # order_by = self.request.query_params.get("order_by", None)
        # self.order_by=order_by
        # if order_by=="value":
        #     if rev == "DESC":
        #         return queryset.order_by("-value","-plays")
        #     return queryset.order_by("value","plays")
        #
        # if rev == "DESC":
        #     return queryset.order_by("-plays", "-value")
        # return queryset.order_by("plays","value")
        return queryset


    def get_group_by(self):
        daily = TruncDate("date", output_field=DateField())
        hourly = Concat(TruncDate("date"), Value(" "), ExtractHour("date"), Value(":00:00"),
                        output_field=DateTimeField())
        monthly = Concat(ExtractYear("date"), Value("-"), ExtractMonth("date"), Value("-01"))
        country=F("radio__country")
        yearly = ExtractYear("date")
        radio = Concat(F("radio_id"), Value("-"), F("radio__name"), output_field=CharField())
        device = Concat(F("device_id"), Value("-"), F("device__name"), output_field=CharField())
        song = Concat(F("song_id"), Value("-"), F("song__track_id"), output_field=CharField())

        if self.format == "daily":
            return daily
        elif self.format == "hourly":
            return hourly
        elif self.format == "monthly":
            return monthly
        elif self.format == "yearly":
            return yearly
        elif self.format == "device":
            return device
        elif self.format == "radio":
            return radio
        elif self.format == "song":
            return song
        elif self.format == "country":
            return country
        else:
            raise MyCustomException("Error", 400)


    def get_statistics_format(self):
        format = self.kwargs['type']
        if format not in self.formats:
            raise MyCustomException("Invalid type , choose one of the following [%s]" % (
                reduce(lambda x, y: "%s ,%s" % (x, y), self.formats)), 400)
        self.format = format

    def get_formatted_response_data(self,data):
        # print("Thed daya is ",data)
        # print("getting response data")
        # if self.format=="song" and self.order_by==None:
        #     ###Add asolute url to the
        #     return map(self.return_full_image_url,self.group_data(data=data))
        #
        # if self.format=="song":
        #     return map(self.return_full_image_url,data)
        #
        # elif self.format in self.append_county_names:
        #     return map(self.radio_add_county_full_name,data)

        return data
