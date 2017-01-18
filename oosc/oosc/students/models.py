from django.db import models
from oosc.classes.models import Classes
from oosc.schools.models import Schools

# Create your models here.
class Students(models.Model):
    GENDERS = (('ML', 'MALE'), ('FM', 'FEMALE'))
    student_id    = models.IntegerField(default=0,null=True,blank=True)
    #school_id     = models.ForeignKey(Schools,on_delete = models.CASCADE)
    emis_code     = models.IntegerField(default=0,null=True,blank=True)
    fstname  = models.CharField(max_length=200)
    midname = models.CharField(max_length=200,null=True,blank=True)
    lstname = models.CharField(max_length=200)
    date_of_birth = models.DateField(null=True,blank=True);
    admission_no  = models.IntegerField(default=0,null=True,blank=True)
    class_id      = models.ForeignKey(Classes,on_delete = models.CASCADE) #shows the current class
    gender        = models.CharField(max_length=2,choices=GENDERS, default='ML')
    previous_class    = models.IntegerField(default=0,null=True,blank=True)
    mode_of_transport = models.CharField(max_length=200,null=True,blank=True)
    time_to_school = models.IntegerField(default=0,null=True,blank=True)
    stay_with  = models.CharField(max_length=200,null=True,blank=True)
    household  = models.IntegerField(default=0,null=True,blank=True)             #people in the same house
    meals_per_day   = models.IntegerField(default=0,null=True,blank=True)
    not_in_school_before = models.BooleanField(default=False)   #reason for not being in school before
    emis_code_histories = models.CharField(max_length=200,null=True,blank=True)
    total_attendance =models.IntegerField(default=0,null=True,blank=True)
    total_absents=models.IntegerField(default=0,null=True,blank=True)
    last_attendance=models.DateField(null=True,blank=True)

    def __str__(self):
        return self.lstname
