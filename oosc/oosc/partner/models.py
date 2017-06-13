from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Partner(models.Model):
    user=models.OneToOneField(User)
    name=models.CharField(max_length=90)


    def __str__(self):
        return self.name
