from rest_framework import serializers
from oosc.attendance.models import Attendance
from oosc.students.serializers import SimpleStudentSerializer
from oosc.students.models import Students
class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ('id','student','date','status','cause_of_absence','_class')

class AbsentStudentSerializer(serializers.ModelSerializer):
    student=serializers.SerializerMethodField()
    class Meta:
        model=Attendance
        fields=('student',)

    def get_student(self,obj):
        stud=Students.objects.filter(id=obj.student_id)
        if(stud.exists()):
            return SimpleStudentSerializer(stud[0]).data
        return None
    def to_representation(self, instance):
        return self.get_student(instance)