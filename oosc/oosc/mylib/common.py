from django.db.models import Value
from django.db.models.expressions import F
from django.db.models.functions import Concat
from rest_framework.exceptions import APIException
from django.db.models import Q, DateField

import uuid
from datetime import datetime,timedelta

from oosc.classes.models import PublicHoliday


def get_random():
    return uuid.uuid1()

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
    return get_stream_name(obj)

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
                    ### Loop therough the names am checking against names STD, CLASS
                    for g in names:
                        if nnm in g:
                            del nems[nems.index(nnm)]


                str_name=nems[-1]


    return "CLASS %s %s" %(bs,str_name)


def make_attendance_history():










