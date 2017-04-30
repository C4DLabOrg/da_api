from django.db import models
from oosc.students.models import Students
from oosc.stream.models import Stream
# Create your models here.
class Promotions(models.Model):
    prev_class=models.ForeignKey(Stream, related_name="previous_class")
    student_id = models.ForeignKey(Students,on_delete=models.CASCADE)
    next_class = models.ForeignKey(Stream, related_name="next_class")

    def __str__(self):
        return "%s to %s" % (self.prev_class,self.next_class)
