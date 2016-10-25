from django.db import models
from oosc.counties.models import Counties

# Create your models here.

class Constituencies(models.Model):
<<<<<<< HEAD
    constituency = models.CharField(max_length=200)
    county_id = models.ForeignKey(Counties, on_delete=models.CASCADE)

    def __str__(self):
        return ('constituency')
=======
    cons_name = models.CharField(max_length=200)
    county_id = models.ForeignKey(Counties, on_delete=models.CASCADE)
>>>>>>> f6fa739de7087389f448ff1647ab1cd8a3023aa1
