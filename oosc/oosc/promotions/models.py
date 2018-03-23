from django.core.exceptions import NON_FIELD_ERRORS
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


class PromoteSchoolManager(models.Manager):
    def get_queryset(self):
        return super(PromoteSchoolManager, self).get_queryset()

class PromoteSchool(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    school=models.ForeignKey(Schools)
    completed=models.BooleanField(default=False)
    year = models.PositiveSmallIntegerField(max_length=4)
    graduates_class=models.ForeignKey(GraduatesStream,null=True,blank=True)
    objects=PromoteSchoolManager()

    # class Meta:
    #     unique_together = ('school', 'year')
        # error_messages = {
        #     NON_FIELD_ERRORS: {
        #         'unique_together': "%(model_name)s's %(field_labels)s are not unique.",
        #     }
        # }

    def __str__(self):
        return "%s (%s) "%(self.school.school_name,self.year)

    def complete(self):
        #Get all the promotions and order them from class 8
        proms=list(PromoteStream.objects.filter(promote_school_id=self.id).order_by("-prev_class___class"))

        # for p in proms:print(p.next_class.class_name)

        #Graduate class 8 and make the inactive
        Students.objects.filter(class_id__school_id=self.school,class_id___class='8').update(active=False,class_id=None,graduated=True,graduates_class_id=self.graduates_class_id)
        # For the rest starting with class & change the prev class id to next_class id
        for p in proms:
            d=Students.objects.filter(class_id_id=p.prev_class_id).update(class_id_id=p.next_class_id)
            p.completed = True
            p.save()
            # print (d)
            # print (p.next_class.class_name, d)
        self.completed=True
        self.save()

    def undo(self):
        proms = list(PromoteStream.objects.filter(promote_school_id=self.id).order_by("prev_class___class"))
        for p in proms:
            d=Students.objects.filter(class_id_id=p.next_class_id).update(class_id_id=p.prev_class_id)
            p.completed=False
            p.save()
            # print (p.next_class.class_name, d)
        ##revert Class 8
        cl8_id=proms[-1].next_class.id
        # print (cl8_id)
        d=Students.objects.filter(graduates_class_id=self.graduates_class_id).update(active=True,
                                                                                              class_id=cl8_id,
                                                                                              graduated=False,
                                                                                             )

        # print ("reverted ",d)
        self.completed = False
        self.save()

    # def delete(self):
    #     if self.completed:
    #         self.undo()
    #     super(PromoteSchool, self).delete()

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
        return "%s to %s" %(self.prev_class.class_name,self.next_class.class_name)
