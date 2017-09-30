from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Partner(models.Model):
    user=models.OneToOneField(User)
    name=models.CharField(max_length=90,unique=True)
    phone=models.CharField(max_length=20,null=True,blank=True)


    def __str__(self):
        return self.name
