from django.db import models
from oosc.schools.models import Schools

# Create your models here.
class Classes(models.Model):
    class_name = models.CharField(max_length = 200, default="none")
    school_id = models.ForeignKey(Schools, on_delete=models.CASCADE)
    teacher_id = models.IntegerField(default = 0)

    def __str__(self):
        return ('class_name')
