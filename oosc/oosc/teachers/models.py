from django.db import models
from oosc.subjects.models import Subjects
from oosc.schools.models import Schools

# Create your models here.
class Teachers(models.Model):

    name = models.CharField(max_length=200)
    phone_no = models.IntegerField(default=0)
    type = models.IntegerField(default=0)
    age  = models.DateTimeField();
    gender = models.CharField(max_length=200)
    tsc_no = models.CharField(max_length=200)
    bom_no = models.CharField(max_length=200)
    qualifications = models.CharField(max_length=200)
    subjects = models.ManyToManyField(Subjects)
    school_id = models.ForeignKey(Schools, on_delete=models.CASCADE)
    date_started_teaching = models.DateTimeField()
    joined_current_school = models.DateTimeField()

    def __str__(self):
        return ('name')
