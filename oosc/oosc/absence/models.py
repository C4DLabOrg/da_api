from __future__ import unicode_literals

from django.db import models
from oosc.students.models import Students
from oosc.reason.models import Reason
# Create your models here.
from oosc.stream.models import Stream


class Absence(models.Model):
    student=models.ForeignKey(Students)
    _class=models.ForeignKey(Stream)
    #_class=models.CharField(max_length=20,default='y')
    reasons=models.ManyToManyField(Reason,null=True,blank=True)
    status=models.BooleanField(default=True)
    date_from=models.DateField()
    date_to=models.DateField(null=True,blank=True)
