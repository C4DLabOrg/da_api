from django.db import models
from oosc.counties.models import Counties

# Create your models here.

class Constituencies(models.Model):
    cons_name = models.CharField(max_length=200)
    county_id = models.ForeignKey(Counties, on_delete=models.CASCADE)
