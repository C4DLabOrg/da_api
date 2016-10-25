from django.db import models

# Create your models here.
class Promotions(models.Model):

    student_id = models.IntegerField(default=0)
    promotions = models.IntegerField(default=0)
