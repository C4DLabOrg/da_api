from django.http.response import HttpResponseBase
from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from rest_framework.response import Response

from oosc.mylib.common import MyDjangoFilterBackend, StandardresultPagination, MyCustomException
from oosc.reason.models import Reason
from oosc.reason.serializers import ReasonSerializer
from oosc.students.models import Students
from django.db.models import F, Count, DateField, DateTimeField, CharField, IntegerField, TextField, When, Q, Case
from django.db.models import Value
from django.db.models.functions import Concat, Cast
from django.db.models.functions import ExtractHour
from django.db.models.functions import ExtractMonth
from django.db.models.functions import ExtractYear
from django.db.models.functions import TruncDate

from oosc.students.views import EnrollmentSerializer
import json

class ListCreatereason(generics.ListCreateAPIView):
    queryset = Reason.objects.all()
    serializer_class = ReasonSerializer



class ListReasonForDropout(generics.ListAPIView):
    serializer_class = EnrollmentSerializer
    queryset = Students.objects.filter(active=False)
    filter_backends = (MyDjangoFilterBackend,)
    pagination_class = None
    myformats = ["class", "gender","partner", "county","reason","yearly","monthly","daily","school"]
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
        studs = self.filter_queryset(Students.objects.filter(active=False))
        format = self.kwargs['type']

        if format not in self.myformats:
            raise MyCustomException("Allowed types are {}".format(",".join(self.myformats)))

        at = self.get_formated_data(studs, format=format)
        # print(at)
        return at

    def resp_fields(self):
        # lst = str(datetime.now().date() - timedelta(days=365))
        # enrolledm = Count(Case(When(Q(date_enrolled__gte=lst) & Q(gender="M"), then=1), output_field=IntegerField(), ))
        enrolledm = Case(
            When(Q(is_oosc=False) & Q(gender="F") & Q(active=False), then=Value("dropout_old_females")),
            When(Q(is_oosc=False) & Q(gender="M") & Q(active=False), then=Value("dropout_old_males")),
            When(Q(is_oosc=False) & Q(gender="M") & Q(active=False), then=Value("dropout_old_males")),
            When((Q(is_oosc=True) & Q(gender="M") & Q(active=False)), then=Value("dropout_enrolled_males")),
            When(Q(is_oosc=True) & Q(active=False) & Q(gender="F"), then=Value("dropout_enrolled_females")),
            default=Value("others")
            , output_field=CharField()
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
        enrolledm = self.resp_fields()
        # enrolledm, oldf, enrolledf, oldm,dropoldm,dropoldf,dropnewm,dropnewf = self.resp_fields()
        outp = Concat("month", Value(''), output_field=CharField())
        at = data.annotate(month=self.get_format(format=format)).values("month") \
            .order_by('month', 'type').annotate(type=enrolledm).annotate(count=Count("type"))
        return self.filter_formatted_data(format=format, data=at)

    def filter_formatted_data(self, format, data):
        # if format=="monthly":
        #     print("Sorting the monthlyv data .")
        #     return sorted(data,key=lambda x: parse_date(x["month"]),reverse=True)
        return data.order_by("month")

    def group(self, data):
        data_dict = json.loads(json.dumps(data))
        values = [d["month"] for d in data_dict]
        values = list(set(values))
        output = []
        for a in values:
            if a == "": continue
            value_obj = {}
            value_obj["value"] = a
            # Try getting the value object
            value_objs = [p for p in data_dict if p["month"] == a]
            total_attrs = ["old_males", "old_females", "enrolled_males", "enrolled_females"]
            dropout_total_attrs = ["dropout_old_males", "dropout_old_females", "dropout_enrolled_males",
                                   "dropout_enrolled_females"]
            dropout_total = 0
            total = 0
            for b in value_objs:
                if b["type"] in total_attrs:
                    total += b["count"]
                elif b["type"] in dropout_total_attrs:
                    dropout_total += b["count"]
                value_obj[b["type"]] = b["count"]
            value_obj["total"] = total
            value_obj["dropout_total"] = dropout_total
            output.append(self.confirm_obj(value_obj))

        return sorted(output, key=lambda k: k.get('value', 0), reverse=False)

    def confirm_obj(self, obj):
        attrs = ["dropout_old_females", "dropout_old_males", "dropout_enrolled_females"
            , "dropout_enrolled_males", "old_males", "old_females", "enrolled_males", "enrolled_females"]
        for at in attrs:
            try:
                obj[at]
            except:
                obj[at] = 0

        return obj

    def paginate_queryset(self, queryset):
        self.fakepaginate = True
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
        response.data = self.group(response.data)
        # If it does not use pagination and require fake pagination for response
        if self.fakepaginate:
            data = response.data
            resp = {}
            resp["count"] = len(data)
            resp["next"] = None
            resp["prev"] = None
            resp["results"] = data
            response.data = resp
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

    def get_format(self, format):
        daily = Concat(TruncDate("modified"), Value(''), output_field=CharField(), )
        monthly = Concat(ExtractYear("modified"), Value('-'), ExtractMonth('date_enrolled'), Value('-1'),
                         output_field=DateField(), )

        # monthly= Concat(Value('1/'), ExtractMonth('date_enrolled'), Value('/'), ExtractYear("date_enrolled"),
        #               output_field=CharField(), )

        if (format == "monthly"):
            return monthly
        elif format == "daily":
            return daily
        elif format == "yearly":
            return ExtractYear('modified')
        elif format == "gender":
            return Value("gender", output_field=CharField())
        elif format == "school":
            id = Cast("class_id__school_id", output_field=TextField())
            return Concat("class_id__school__school_name", Value(','), id, output_field=CharField())
        elif format == "stream":
            return Concat("class_id__class_name", Value(''), output_field=CharField())
        elif format == "partner":
            return Concat("class_id__school__partners", Value('-'),
                          "class_id__school__partners__name", output_field=CharField())

        elif format=="reason":
            return F("dropout_reason")
        elif format == "county":
            return Concat("class_id__school__zone__subcounty__county__county_name", Value(''), output_field=CharField())
        elif format == "class":
            id = Cast("class_id", output_field=TextField())
            return Concat("class_id___class", Value(''), output_field=CharField())
        else:
            return monthly

