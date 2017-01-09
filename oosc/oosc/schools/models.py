from django.db import models
from oosc.constituencies.models import Constituencies
from django.contrib.auth.models import User
#from oosc.teachers.models import Teachers
# Create your models here.
class Schools(models.Model):
    school_code = models.IntegerField(default=0)
    school_name = models.CharField(max_length = 200, default="schoolname")
    geo_cordinates  = models.CharField(max_length = 200)
    emis_code   = models.IntegerField(default = 0)
    constituency = models.ForeignKey(Constituencies, on_delete = models.CASCADE)
    source_of_water = models.CharField(max_length = 200)
    headteacher = models.OneToOneField(User,related_name="headteacher",null=True,blank=True)
    phone_no    = models.IntegerField(default=0)

    def __str__(self):
        return self.school_name
