from django.db import models

# Create your models here.
class Teachers(models.Model):

    id   = models.IntegerField(default=0)
    name = models.CharField(max_length=200)
    phone_no = models.IntegerField(default=0)
    type = models.IntegerField(default=0)
    age  = models.DateTimeField();
    gender = models.CharField(max_length=200)
    tsc_number = models.CharField(max_length=200)
    bom_number = models.CharField(max_length=200)
    qualifications = models.CharField(max_length=200)
    subjects = models.CharField(max_length=200)
    date_started_teaching = models.DateTimeField()
    joined_current_school = models.DateTimeField()
