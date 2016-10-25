from django.db import models
from oosc.constituencies.models import Constituencies

# Create your models here.
class Schools(models.Model):
    school_code = models.IntegerField(default=0)
    school_name = models.CharField(max_length = 200, default="schoolname")
    geo_cordinates  = models.CharField(max_length = 200)
    emis_code   = models.IntegerField(default = 0)
    constituency = models.ForeignKey(Constituencies, on_delete = models.CASCADE)
    source_of_water = models.CharField(max_length = 200)
    headteacher = models.CharField(max_length=200)
    phone_no    = models.IntegerField(default=0)

    def __str__(self):
        return ('school_name')
