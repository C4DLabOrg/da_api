from django.db import models
from oosc.students.models import Students

# Create your models here.
class Promotions(models.Model):
    promotion_id = models.IntegerField(default = 0)
    student_id = models.ForeignKey(Students,on_delete=models.CASCADE)
    promotions = models.IntegerField(default=0)

    def __str__(self):
        return ('promotions')
