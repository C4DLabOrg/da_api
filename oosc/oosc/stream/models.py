from django.db import models

from oosc.classes.models import Classes
from oosc.schools.models import Schools
from oosc.teachers.models import Teachers
# Create your models here.
class Stream(models.Model):

    class_name = models.CharField(max_length = 200)
    school = models.ForeignKey(Schools, on_delete=models.CASCADE,related_name="streams")
    _class = models.ForeignKey(Classes)
    teachers = models.ManyToManyField(Teachers,related_name="class_teachers",null=True,blank=True)
    #teacher_id=models.IntegerField(max_length=50)
    def __str__(self):
        return self.class_name+" ("+self.school.school_name+")"


    def save(self, force_insert=False, force_update=False,using=None):
        self.class_name = self.class_name.upper()
        super(Stream, self).save(force_insert, force_update)

    def get_the_class(self):
        m = list(self.class_name)
        for n in m:
            if n.isdigit():
                print n
                return n

class GraduatesStream(models.Model):
    school = models.ForeignKey(Schools, on_delete=models.CASCADE, related_name="graduate_streams")
    year=models.PositiveSmallIntegerField(max_length=4)
    class_name = models.CharField(max_length=200,null=True,blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together=('school','year')




