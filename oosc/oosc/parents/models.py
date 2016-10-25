from django.db import models
from oosc.students.models import Students

# Create your models here.

class Parents(models.Model):
    parents_name = models.CharField(max_length=200)
    phone_no   = models.IntegerField(default=0)
    student_id = models.ForeignKey(Students,on_delete=models.CASCADE)
<<<<<<< HEAD

    def __str__(self):
        return ('parents_name')
=======
>>>>>>> f6fa739de7087389f448ff1647ab1cd8a3023aa1
