from django.db import models

# Create your models here.

class Counties(models.Model):
    #models.ForeignKey(Question, on_delete=models.CASCADE)
    county_id = models.IntegerField(default=0)
    county_name = models.CharField(max_length=200)
