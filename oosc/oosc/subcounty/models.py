from __future__ import unicode_literals

from django.db import models
from oosc.counties.models import Counties

# Create your models here.
class SubCounty(models.Model):
    county=models.ForeignKey(Counties,related_name="subcounties")
    name=models.CharField(max_length=50)

    def __str__(self):
        return self.name
