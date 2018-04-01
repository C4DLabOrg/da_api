from django.db import models
#from oosc.teachers.models import Teachers
from django.db.models import Q, DateField
from django.db.models.expressions import Value, F
from django.db.models.functions import Concat

from oosc.classes.models import PublicHoliday
from oosc.subcounty.models import SubCounty
from oosc.zone.models import Zone
from django.contrib.auth.models import User

#from oosc.teachers.models import Teachers
# Create your models here.
from oosc.partner.models import Partner

from datetime import datetime, date, timedelta

# from oosc.schools.models import Term
# t=Term.objects.get(id="12018")
# t.get_term_dates()

class Schools(models.Model):
    LEVELS=(('PRIMARY','Primary'),('SECONDARY','Secondary'))
    STATUS=(('PUBLIC','Public'),('PRIVATE','Private'))
    school_code = models.IntegerField(default=0,null=True,blank=True)
    school_name = models.CharField(max_length = 200, )
    latitude  = models.FloatField(null=True,blank=True)
    longitude=models.FloatField(null=True,blank=True)
    emis_code   = models.BigIntegerField(unique=True)
    zone = models.ForeignKey(Zone,blank=True,null=True, on_delete = models.SET_NULL)
    source_of_water = models.CharField(max_length = 200,null=True,blank=True)
    headteacher = models.OneToOneField(User,related_name="headteacher",null=True,blank=True)
    phone_no    = models.IntegerField(default=0,)
    subcounty=models.ForeignKey(SubCounty,null=True,blank=True)
    level=models.CharField(choices=LEVELS,max_length=50,default='PRIMARY')
    status=models.CharField(choices=STATUS,max_length=50,default='PUBLIC')
    partners=models.ManyToManyField(Partner,null=True,blank=True,related_name="schools")
    partner_conflict=models.BooleanField(default=False)

    def __str__(self):
        return self.school_name



class Term(models.Model):
    TERMS=(('1','1st Term'),('2','2nd Term'),('3','3rd Term'))
    id=models.CharField(primary_key=True,max_length=30)
    year=models.IntegerField(default=datetime.now().year)
    term=models.CharField(max_length=2,choices=TERMS)
    start_date=models.DateField()
    end_date=models.DateField()
    # objects=TermManager()



    def get_term_dates(self,year=None):
        #Get the current year or any other year
        thisyear=datetime.now().year if year==None else year
        thedate = self.start_date
        ###Exclude holidays and sny days set
        theholidays=list(PublicHoliday.objects.exclude(Q(year__lt=thisyear) | Q(year__gt=thisyear)).\
            annotate(date=Concat(Value(thisyear),Value("-"),F("month"),Value("-"),F("day"),output_field=DateField()))\
            .values_list("date",flat=True))
        holidays=[datetime.strptime(d,"%Y-%m-%d").date() for d in theholidays]
        days=[]

        while thedate  !=  self.end_date:
            if thedate.weekday() < 5 and thedate not in holidays:
                days.append(thedate)
            else:
                pass
                # print ("Weekend %s"%(thedate))
            thedate+=timedelta(days=1)
            # print ("New Date ",thedate)
        return days







