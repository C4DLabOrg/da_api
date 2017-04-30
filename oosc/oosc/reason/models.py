from __future__ import unicode_literals

from django.db import models
from oosc.students.models import Students
# Create your models here.
class Reason(models.Model):
    name=models.CharField(max_length=140)


