from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
from oosc.mylib.queryset2excel import exportcsv


class Partner(models.Model):
    user=models.OneToOneField(User)
    name=models.CharField(max_length=90,unique=True)
    phone=models.CharField(max_length=20,null=True,blank=True)
    test=models.BooleanField(default=False)
    last_data_upload=models.DateTimeField(null=True,blank=True)

    def __str__(self):
        return self.name


class PartnerAdmin(models.Model):
    user = models.OneToOneField(User)
    name = models.CharField(max_length=90, unique=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    test = models.BooleanField(default=False)
    partners=models.ManyToManyField(Partner,null=True,blank=True,related_name="partner_admins")

    def __str__(self):
        return self.name
# filename="test"
# queryset=[{"school_title":"Warugara","count":4}]
# headers=[{"name":"School Title","value":"school_title"},{"name":"Students Count","value":"count"},{"name":"Test  Final","value":"test"}]
# path=exportcsv(filename=filename,queryset=queryset,headers=headers,title="Schools")
# print(path)
# print("The path taken by the export")
