from django.db import models

# Create your models here.
class Schools(models.Model):
    school_id   = models.IntegerField(default=0)
    school_code = models.IntegerField(default=0)
    school_name = models.CharField(max_length = 200)
    geo_cordinates  = models.IntegerField(default=0)
    emis_code   = models.IntegerField(default=0)
    const_id = models.IntegerField(default=0)
    source_of_water = models.CharField(max_length = 200)
