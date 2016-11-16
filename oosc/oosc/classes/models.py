from django.db import models
from oosc.schools.models import Schools
from oosc.teachers.models import Teachers
# Create your models here.
class Classes(models.Model):
    class_name = models.CharField(max_length = 200, default="none")
    school_id = models.ForeignKey(Schools, on_delete=models.CASCADE)
    teacher_id = models.ForeignKey(Teachers,related_name="class_teacher")
    #teacher_id=models.IntegerField(max_length=50)
    def __str__(self):
        return self.class_name
