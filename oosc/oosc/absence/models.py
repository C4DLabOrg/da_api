from __future__ import unicode_literals

from django.db import models

from oosc.students.models import Students
from oosc.reason.models import Reason
# Create your models here.
class Absence(models.Model):
    student=models.ForeignKey(Students)
    reasons=models.ManyToManyField(Reason,null=True,blank=True)
    status=models.BooleanField(default=False)
    date_from=models.DateField()
    date_to=models.DateField()
