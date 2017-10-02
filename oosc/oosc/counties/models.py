from django.db import models

# Create your models here.

class Counties(models.Model):
    county_name = models.CharField(max_length=200)
    lat=models.FloatField(null=True,blank=True)
    lng=models.FloatField(null=True,blank=True)
    def __str__(self):
        return self.county_name
