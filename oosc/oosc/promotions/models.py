from django.db import models

from oosc.schools.models import Schools
from oosc.students.models import Students
from oosc.stream.models import Stream, GraduatesStream


# Create your models here.

class Promotions(models.Model):
    prev_class=models.ForeignKey(Stream, related_name="previous_class")
    student_id = models.ForeignKey(Students,on_delete=models.CASCADE)
    next_class = models.ForeignKey(Stream, related_name="nexti_class")

    def __str__(self):
        return "%s to %s" % (self.prev_class,self.next_class)



class PromoteSchool(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    school=models.ForeignKey(Schools)
    completed=models.BooleanField(default=False)
    year = models.PositiveSmallIntegerField(max_length=4)
    graduates_class=models.ForeignKey(GraduatesStream,null=True,blank=True)

    class Meta:
        unique_together = ('school', 'year')

    def __str__(self):
        return "%s (%s) "%(self.school.school_name,self.year)

    def promote(self):
        proms=self.promotions.all()
        # for pr in proms:
        print (proms)

    def save(self,  *args, **kwargs):
        if self.id is None:
            g=GraduatesStream(school=self.school,year=self.year)
            g.save()
            self.graduates_class_id=g.id
        else:
            GraduatesStream.objects.filter(id=self.graduates_class_id).update(school=self.school,year=self.year)
        super(PromoteSchool, self).save(*args, **kwargs)


class PromoteStream(models.Model):
    prev_class=models.ForeignKey(Stream,related_name="prev_class")
    next_class=models.ForeignKey(Stream,related_name="next_class")
    completed=models.BooleanField(default=False)
    created=models.DateTimeField(auto_now_add=True)
    modified=models.DateTimeField(auto_now=True)
    promote_school=models.ForeignKey(PromoteSchool,related_name="stream_promotions")


    def __str__(self):
        return "%s to %s" %(self._class.class_name,self.next_class.class_name)
