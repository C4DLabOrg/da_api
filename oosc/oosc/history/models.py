from __future__ import unicode_literals

from django.db import models
from oosc.students.models import Students
from oosc.stream.models import Stream
from datetime import datetime
# Create your models here.

class History(models.Model):
    LEFT_CHOICES=(('DROP','Dropout'),('TRANS','Transfer'))
    student=models.ForeignKey(Students)
    _class=models.ForeignKey(Stream)
    joined=models.DateField(null=True,blank=True)
    joined_description=models.CharField(max_length=400,null=True,blank=True)
    left=models.DateField(null=True,blank=True)
    created=models.DateTimeField(auto_now_add=True)
    modified=models.DateTimeField(auto_now=True)
    left_description=models.CharField(choices=LEFT_CHOICES,max_length=10,null=True,blank=True)
