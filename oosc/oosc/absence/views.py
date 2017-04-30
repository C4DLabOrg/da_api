from django.shortcuts import render

# Create your views here.
from oosc.absence.models import Absence
from oosc.absence.serializers import AbsenceSerializer
from rest_framework import generics
from oosc.attendance.models import Attendance
from django.db.models import Count,Case,When,IntegerField,Q,Value,CharField,TextField
from datetime import datetime,timedelta
from oosc.absence.models import Absence
from oosc.students.models import Students
from oosc.config.settings import DROPOUT_MIN_COUNT
from oosc.schools.models import Schools


class GetEditAbsence(generics.RetrieveUpdateAPIView):
    queryset = Absence.objects.all()
    serializer_class = AbsenceSerializer
#
# class GetTheDropOuts()
#from oosc.absence.views import GenerateReport as d

#Calculating the droupouts weekly
def d(school):
    now=datetime.now().date()
    then=now-timedelta(days=14)
    attend=Attendance.objects.all().filter(date__range=[then,now],student__class_id__school_id=school)
    attendances= attend.order_by('student_id').values("student_id").annotate(present_count=Count(Case(When(status=1,then=1),output_field=IntegerField())),absent_count=Count(Case(When(status=0,then=1),output_field=IntegerField())))
    ##Filter for students with 0 present (Not a single attendance in the last two weeks)
    drops=attendances.filter(present_count=0)
    #print ([[len(drops),len(attendances),len(Attendance.objects.all().values("student_id").annotate(count=Count(Case(When(status=1,then=1),output_field=IntegerField())))),d] for d in drops])
    #print([d["student_id"] for d in drops])

    ## Get Students absent from school for the last 2 weeks continous
    students=[d["student_id"] if d["absent_count"]>=DROPOUT_MIN_COUNT else None for d in drops]
    while None in students:students.remove(None)
    ##Get Students already with an open absence record
    former_absents=[s.student_id for s in Absence.objects.filter(status=True,student_id__in=students)]

    ##Remove students with an existing open absence record
    [students.remove(d) if d  in students else '1' for d in former_absents]
    ##Get the students in the list
    students=Students.objects.filter(id__in=students)
    ##Create absence records for students without open Absence records
    absences=[Absence(student_id=d.id,_class=d.class_id,status=True,date_from=then) for d in students]
    ##Bulk Create the records
    Absence.objects.bulk_create(absences)
    #print(len(absences),len(students))

def GenerateReport():
    schools=[sh.id for sh in Schools.objects.all()]
    for s in schools:
        d(s)
        print (s)





