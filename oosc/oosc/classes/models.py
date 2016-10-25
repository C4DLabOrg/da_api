from django.db import models

# Create your models here.
class Classes(models.Model):
    class_id = models.IntegerField(default  = 0)
    school_id = models.IntegerField(default = 0)
    teacher_id = models.IntegerField(default = 0)
