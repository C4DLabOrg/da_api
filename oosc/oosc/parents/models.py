from django.db import models

# Create your models here.

class Parents(models.Model):
    parents_id   = models.IntegerField(default=0)
    parents_name = models.CharField(max_length=200)
    phone_no   = models.IntegerField(default=0)
    student_id = models.IntegerField(default=0)
