from django.db import models

# Create your models here.

class Counties(models.Model):
    county_name = models.CharField(max_length=200)

    def __str__(self):
        return ('county_name')
