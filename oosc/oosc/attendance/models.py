from django.db import models

# Create your models here.
class Attendance(models.Model):
    attendance_id = models.IntegerField(default = 0)
    student_id  = models.IntegerField(default = 0)
    date    = models.DateTimeField()
    status  = models.IntegerField(default = 0) #assuming 1 is present 0 is absent
    cause_of_absence = models.CharField(max_length = 200)
    class_id = models.IntegerField(default=0)
    school_id = models.IntegerField(default=0)
