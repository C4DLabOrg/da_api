from django.db import models

from oosc.classes.models import Classes
from oosc.schools.models import Schools
from oosc.teachers.models import Teachers
# Create your models here.
class Stream(models.Model):

    class_name = models.CharField(max_length = 200)
    school = models.ForeignKey(Schools, on_delete=models.CASCADE)
    _class = models.ForeignKey(Classes)
    teachers = models.ManyToManyField(Teachers,related_name="class_teachers",null=True,blank=True)
    #teacher_id=models.IntegerField(max_length=50)
    def __str__(self):
        return self.class_name+" ("+self.school.school_name+")"

    def get_the_class(self):
        m = list(self.class_name)
        for n in m:
            if n.isdigit():
                print n
                return n



