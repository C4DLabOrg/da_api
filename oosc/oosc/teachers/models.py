from django.db import models
from oosc.subjects.models import Subjects
from oosc.schools.models import Schools
from django.contrib.auth.models import User
# Create your models here.
class Teachers(models.Model):
    GENDERS = (('M', 'MALE'), ('F', 'FEMALE'))
    TEACHER_TYPE=(('TSC','TSC'),('BRD','BOARD'))
    QUALIFICATIONS=(('UNI','UNIVERSITY'),('COL','COLLEGE'))
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    fstname=models.CharField(max_length=45)
    lstname = models.CharField(max_length=45)
    phone_no = models.CharField(max_length=20)
    teacher_type = models.CharField(max_length=3,choices=TEACHER_TYPE, default='TSC')
    birthday  = models.DateField(null=True,blank=True)
    gender = models.CharField(max_length=2,choices=GENDERS,default='ML')
    tsc_no = models.CharField(max_length=200,null=True,blank=True)
    bom_no = models.CharField(max_length=200,null=True,blank=True)
    qualifications = models.CharField(max_length=3,choices=QUALIFICATIONS,default='COL',null=True,blank=True)
    # subjects = models.ManyToManyField(Subjects,null=True,blank=True)
    school = models.ForeignKey(Schools, on_delete=models.CASCADE)
    date_started_teaching = models.DateField(null=True,blank=True)
    joined_current_school = models.DateField(null=True,blank=True)
    headteacher=models.BooleanField(default=False)
    active=models.BooleanField(default=True)

    def __str__(self):
        return self.user.username+"   ("+self.school.school_name+")"
