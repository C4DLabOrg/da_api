from django.db import models

# Create your models here.

class Subjects(models.Model):
    subject_id   = models.IntegerField(default=0)
    subject_name = models.CharField(max_length=200)
