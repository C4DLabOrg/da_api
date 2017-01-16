from __future__ import unicode_literals

from django.db import models
from oosc.subcounty.models import SubCounty
from oosc.counties.models import Counties
# Create your models here.
class Zone(models.Model):
    name=models.CharField(max_length=50)
    county=models.ForeignKey(Counties)
    subcounty=models.ForeignKey(SubCounty)

    def __str__(self):
        return self.name