from django.db import models

# Create your models here.

class Counties(models.Model):
    county_name = models.CharField(max_length=200)
