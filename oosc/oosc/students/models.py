from django.db import models
from oosc.stream.models import Stream
from oosc.schools.models import Schools

# Create your models here.
class Students(models.Model):
    GENDERS = (('M', 'MALE'), ('F', 'FEMALE'))
    student_id    = models.BigIntegerField(null=True,blank=True)
    #school_id     = models.ForeignKey(Schools,on_delete = models.CASCADE)
    emis_code     = models.BigIntegerField(null=True,blank=True)
    fstname  = models.CharField(max_length=200)
    midname = models.CharField(max_length=200,null=True,blank=True)
    lstname = models.CharField(max_length=200,null=True,blank=True)
    date_of_birth = models.DateField(null=True,blank=True)
    date_enrolled=models.DateField(auto_created=True)
    admission_no  = models.BigIntegerField(default=0,null=True,blank=True)
    class_id      = models.ForeignKey(Stream,null=True,blank=True, on_delete = models.CASCADE,related_name="students") #shows the current class
    gender        = models.CharField(max_length=2,choices=GENDERS, default='ML')
    previous_class    = models.IntegerField(default=0,null=True,blank=True)
    mode_of_transport = models.CharField(max_length=200,null=True,blank=True)
    time_to_school = models.CharField(max_length=50,default=0,null=True,blank=True)
    stay_with  = models.CharField(max_length=200,null=True,blank=True)
    household  = models.IntegerField(default=0,null=True)             #people in the same house
    meals_per_day   = models.IntegerField(default=0,null=True,blank=True)
    not_in_school_before = models.BooleanField(default=False)   #reason for not being in school before
    emis_code_histories = models.CharField(max_length=200,null=True,blank=True)
    total_attendance =models.IntegerField(default=0,null=True,blank=True)
    total_absents=models.IntegerField(default=0,null=True,blank=True)
    last_attendance=models.DateField(null=True,blank=True)
    guardian_name=models.CharField(max_length=50,null=True,blank=True)
    guardian_phone=models.CharField(max_length=20,blank=True,null=True)
    active=models.BooleanField(default=True)
    created=models.DateTimeField(auto_now_add=True)
    modified=models.DateTimeField(auto_now=True)
    is_oosc=models.BooleanField(default=False)
    ## Is it an out of school children
    ##
    def __str__(self):
        if self.class_id:
            return self.lstname+" "+self.fstname+"("+self.class_id.class_name+")"
        return self.lstname+" "+self.fstname

    class Meta:
        ordering=['-gender']

    def deactivate(self):
        self.active=False
        self.class_id=None
        # self.class_id_id=11094
        # self.class_id_id=11078

    def activate(self):
        self.active=True


class ImportError:
    def __init__(self,row_number,error_message,row_details):
        self.row_number=row_number
        self.error_message=error_message
        self.row_details=row_details

class ImportResults:
    def __init__(self,errors,total_success,total_fails,total_duplicates):
        self.errors=errors
        self.total_duplicates=total_duplicates
        self.total_success=total_success
        self.total_fails=total_fails

