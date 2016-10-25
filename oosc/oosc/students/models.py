from django.db import models
from oosc.classes.models import Classes
from oosc.schools.models import Schools

# Create your models here.
class Students(models.Model):
    student_id    = models.IntegerField(default=0)
    #school_id     = models.ForeignKey(Schools,on_delete = models.CASCADE)
    emis_code     = models.IntegerField(default=0)
    student_name  = models.CharField(max_length=200)
    date_of_birth = models.DateTimeField();
    admission_no  = models.IntegerField(default=0)
    class_id      = models.ForeignKey(Classes,on_delete = models.CASCADE) #shows the current class
    gender        = models.IntegerField(default=0)
    previous_class    = models.IntegerField(default=0)
    mode_of_transport = models.CharField(max_length=200)
    time_to_school = models.IntegerField(default=0)
    stay_with  = models.CharField(max_length=200)
    household  = models.IntegerField(default=0)             #people in the same house
    meals_per_day   = models.IntegerField(default=0)
    not_in_school_before = models.IntegerField(default=0)   #reason for not being in school before
    emis_code_histories = models.CharField(max_length=200)

    def __str__(self):
        return ('student_name')
