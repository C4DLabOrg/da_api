import re

import pytz
from django.core.paginator import Paginator
from django.db.models import Value, Count
from django.db.models.expressions import F
from django.db.models.functions import Concat
from rest_framework.exceptions import APIException
from django.db.models import Q, DateField
import copy
import uuid
from datetime import datetime,timedelta
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

from oosc.attendance.models import Attendance, AttendanceHistory
from oosc.classes.models import PublicHoliday
from django_filters.rest_framework import FilterSet


from sys import stdout
def get_random():
    return uuid.uuid1()



class StandardresultPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 1000
    page_size_query_param = 'page_size'


def get_dynamic_model_filter_class(model_class):
    # for s in survey.formulas.all().values_list("slug",flat=True):
    #     slugs.append(s)
    # myextra_kwargs = {f.name: {"required": True} for f in model_class._meta.fields if not f.blank}
    class Meta:
        model = model_class
        fields = ("__all__")
        exclude=("image","logo","file")
        # extra_kwargs = myextra_kwargs

    attrs = {"Meta": Meta}
    serializer = type('Response' + model_class.__class__.__name__ + "Filter", (FilterSet,), attrs)
    return serializer

class MyDjangoFilterBackend(DjangoFilterBackend):
    myfilter_class = None

    def get_filter_class(self, view, queryset=None):
        """
        Return the django-filters `FilterSet` used to filter the queryset.
        """

        if self.myfilter_class:
            return self.myfilter_class
        query = getattr(view, 'queryset', None)
        try:
            model = query.model
            filter_model = model
            filter_class = get_dynamic_model_filter_class(model)
            assert issubclass(queryset.model, filter_model), \
                'FilterSet model %s does not match queryset model %s' % \
                (filter_model, queryset.model)
            self.myfilter_class = filter_class
            return filter_class
        except Exception as e:
            print(e)
            raise MyCustomException("The View must inherit from MyDynamicGetSerializerQuerysetModelMixin ")

    def filter_queryset(self, request, queryset, view):
        filter_class = self.get_filter_class(view, queryset)
        if filter_class:
            return filter_class(request.query_params, queryset=queryset).qs
        return queryset

class MyCustomException(APIException):
    status_code = 503
    detail="Service temporarily unavailable, try again later."
    default_detail = 'Service temporarily unavailable, try again later.'
    default_code = 'service_unavailable'

    def __init__(self,message,code=400):
        self.status_code=code
        self.default_detail=message
        self.detail=message


def my_class_name(obj):

    """
    Format the class name to conform to the norms
    :param obj:
    :return:
    """
    # return get_stream_name(obj)

    ####Using regular expression
    try:
        full_name,_class,stream_name=get_stream_name_regex(obj.class_name)
    except:
        full_name=get_stream_name(obj)
    return full_name

def get_bs_number(cl_name):
    for a in cl_name:
        if a.isdigit():
            return a
    return None

def filter_students_by_names(queryset,value):
    names = value.split(" ")
    if len(names) > 2:
        return queryset.filter(
            Q(fstname__icontains=names[0]), Q(midname__icontains=names[1]), Q(lstname__icontains=names[2]))
    elif len(names) == 2:
        return queryset.filter(
            Q(fstname__icontains=names[0]), (Q(lstname__icontains=names[1]) | Q(midname__icontains=names[1])))

    return queryset.filter(
        Q(fstname__icontains=value) | Q(lstname__icontains=value) | Q(midname__icontains=value)
    )


def get_list_of_dates( start_date=None,end_date=None):
    # Get the current year or any other year
    if start_date ==None or end_date ==None:raise MyCustomException("You must include start and end dates",400)
    thisyear = datetime.strptime(start_date,"%Y-%m-%d").year
    thedate = datetime.strptime(start_date,"%Y-%m-%d")
    end_date=datetime.strptime(end_date,"%Y-%m-%d")
    ###Exclude holidays and sny days set
    theholidays = list(PublicHoliday.objects.exclude(Q(year__lt=thisyear) | Q(year__gt=thisyear)). \
                       annotate(
        date=Concat(Value(thisyear), Value("-"), F("month"), Value("-"), F("day"), output_field=DateField())) \
                       .values_list("date", flat=True))
    holidays = [datetime.strptime(d, "%Y-%m-%d").date() for d in theholidays]
    days = []

    while thedate != end_date:
        if thedate.weekday() < 5 and thedate not in holidays:
            days.append(thedate)
        else:
            pass
            # print ("Weekend %s"%(thedate))
        thedate += timedelta(days=1)
        # print ("New Date ",thedate)
    return days

def is_date(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def get_quick_stream_class_name(name):
    replace_words=["std","class","STD","CLASS"]
    num=[f for f in name if f.isdigit()][0]
    for d in replace_words:name=name.replace(d,"")
    name=name.replace(num,"")
    return "CLASS %s%s"%(num,name)

def get_stream_name(obj):
    # print ( "data", type(obj))
    names=['STD','CLASS']
    bs=obj._class if type(obj) is not dict else obj["_class"]
    cl_name=obj.class_name if type(obj) is not dict else obj["class_name"]
    str_name=""
    bs_in_name=False
    name=""
    try:
        ind=cl_name.index(bs)
        bs_in_name=True
    except Exception as e:
        bs_in_name=False

    if bs_in_name:
        nms=cl_name.split(bs)
        str_name=nms[-1] if len(nms) > 1 else bs
    else:
        num=get_bs_number(cl_name)
        if num is not None:
            nms = cl_name.split(num)
            str_name=nms[-1]
        else:
            nems=cl_name.split(" ")
            if len(nems)==1:
                str_name=nems[0]

            else:
                ##Loop through the names found
                for nnm in nems:
                    ### Loop therough the names and checking against names STD, CLASS
                    for g in names:
                        if nnm in g:
                            del nems[nems.index(nnm)]


                str_name=nems[-1]
    return "CLASS %s %s" %(bs,str_name)

def chunked_iterator(queryset, chunk_size=10000):
    paginator = Paginator(queryset, chunk_size)
    for page in range(1, paginator.num_pages + 1):
        for obj in paginator.page(page).object_list:
            yield obj

def get_stream_name_regex(name):
    exp = r"(std|class)? ?([0-9])+ ?(.{1,})?"
    pattern = re.compile(exp, re.IGNORECASE)
    totalresults = pattern.findall(name)

    results = totalresults[0] if len(totalresults) > 0 else None

    if results :
        # print("The results are ", len(results))
        # fullname = "CLASS %s %s" % (results[1], results[2].replace(" ", ""))
        fullname = "CLASS %s %s" % (results[1], results[2])
        _class = results[1].upper()
        stream_name = results[2].upper()
        return fullname.upper(), _class, stream_name
    else:
        print("Failed ",totalresults,results,name)

    return name,"",""



def make_attendance_history():
    # .filter(date=datetime.now().date())
    atts=list(Attendance.objects.values("date","_class","status")\
        .annotate(count=Count("status")).order_by("date","_class"))
    local_tz = pytz.timezone('Africa/Nairobi')
    print (len(atts))
    c=0
    thedate=None
    theclass=None
    for i in atts:
        id=datetime.strftime(i["date"].replace(tzinfo=pytz.utc).astimezone(local_tz),"%Y%m%d")+"%s"%(i["_class"])
        # print (id,)
        if thedate==i["date"] and theclass==i["_class"]:
            pass
        else:
            pobj=filter(lambda x: x["date"] == i["date"] and x["_class"] == i["_class"] and x["status"]==1,copy.deepcopy(atts))
            aobj=filter(lambda x: x["date"] == i["date"] and x["_class"] == i["_class"] and x["status"]==0,copy.deepcopy(atts))
            # print ("stuff",pobj,aobj)
            abss=aobj[0]["count"] if len(aobj) > 0 and "count" in aobj[0] else 0
            pbss=pobj[0]["count"] if len(pobj)>0 and "count" in pobj[0] else 0
            ath = AttendanceHistory(id=id, absent=abss,present=pbss, date=i["date"], _class_id=i["_class"])
            ath.save()
        c=c+1
        stdout.write ("\r%s of %s"%(c,len(atts)))
        stdout.flush()
        thedate=i["date"]
        theclass=i["_class"]


# make_attendance_history()







