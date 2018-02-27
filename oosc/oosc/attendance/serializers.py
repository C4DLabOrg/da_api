from rest_framework import serializers
from oosc.attendance.models import Attendance, AttendanceHistory
from oosc.students.serializers import SimpleStudentSerializer,StudentsSerializer
from oosc.students.models import Students
class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ('id','student','date','created','modified','status','cause_of_absence','_class')

class AbsentStudentSerializer(serializers.ModelSerializer):
    student=serializers.SerializerMethodField()
    class Meta:
        model=Attendance
        fields=('student',)

    def get_student(self,obj):
        stud=Students.objects.filter(id=obj.student_id)
        if(stud.exists()):
            return StudentsSerializer(stud[0]).data
        return None
    def to_representation(self, instance):
        return self.get_student(instance)

class AttendanceHistorySerializier(serializers.ModelSerializer):
    class Meta:
        model=AttendanceHistory
        fields=("__all__")