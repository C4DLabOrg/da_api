from django.db import models

# Create your models here.
class TeachersModel(models.Model):
    name = models.CharField(max_length=100)
    tsc_number = models.CharField(max_length=100)
    gender = models.CharField(max_length=1)

    def __str__(self):
        return self.name
