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
    phone_no = models.IntegerField(default=0)
    teacher_type = models.CharField(max_length=3,choices=TEACHER_TYPE, default='TSC')
    birthday  = models.DateField()
    gender = models.CharField(max_length=2,choices=GENDERS,default='ML')
    tsc_no = models.CharField(max_length=200)
    bom_no = models.CharField(max_length=200)
    headteacher=models.BooleanField()
    qualifications = models.CharField(max_length=3,choices=QUALIFICATIONS,default='COL')
    subjects = models.ManyToManyField(Subjects)
    school = models.ForeignKey(Schools, on_delete=models.CASCADE)
    date_started_teaching = models.DateField()
    joined_current_school = models.DateField()

    def __str__(self):
        return self.user.username
