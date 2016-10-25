from django.db import models

# Create your models here.

class Constituencies(models.Model):
    cons_id = models.IntegerField(default=0)
    #models.ForeignKey(Question, on_delete=models.CASCADE)
    county_id = models.IntegerField(default=0)
    Cons_name = models.CharField(max_length=200)
