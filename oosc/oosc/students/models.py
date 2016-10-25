from django.db import models

# Create your models here.
class Students(models.Model):
    student_id    = models.IntegerField(default=0)
    school_id     = models.IntegerField(default=0)
    emis_code     = models.IntegerField(default=0)
    student_name  = models.CharField(max_length = 200)
    date_of_birth = models.DateTimeField();
    admission_no  = models.IntegerField(default=0)
    class_id      = models.IntegerField(default=0)
    gender        = models.IntegerField(default=0)
    current_class = models.IntegerField(default=0)
    previous_class    = models.IntegerField(default=0)
    mode_of_transport = models.CharField(max_length=200)
    time_to_school = models.IntegerField(default=0)
    stay_with  = models.CharField(max_length=200)
    household  = models.IntegerField(default=0)             #people in the same house
    meals_per_day   = models.IntegerField(default=0)
    not_in_school_before = models.IntegerField(default=0)   #reason for not being in school before
    emis_code_histries = models.CharField(max_length=200)
