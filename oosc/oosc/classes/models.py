from __future__ import unicode_literals

from django.db import models

# Create your models here.



class Classes(models.Model):
    name=models.CharField(max_length=3,primary_key=True)
    created=models.DateTimeField(auto_now=True)
    modified=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class PublicHoliday(models.Model):
    name=models.CharField(max_length=50)
    # date=models.DateField()
    year=models.IntegerField(null=True,blank=True)
    one_time=models.BooleanField(default=False)
    month=models.IntegerField()
    day=models.IntegerField()


    def __str__(self):
        return "%s-%s" %(self.name,self.year)
