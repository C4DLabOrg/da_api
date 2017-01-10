from rest_framework import serializers
from oosc.classes.models import Classes
from rest_framework import serializers
from oosc.students.models import Students
from oosc.students.serializers import SimpleStudentSerializer
class ClassesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classes
        fields = ('class_name','school_id','teacher_id')
class StudentsClassSerializer(serializers.ModelSerializer):
    students=serializers.SerializerMethodField()
    class Meta:
        model=Classes
        fields=('id','class_name','students')

    def get_students(self,obj):
        queryset=Students.objects.filter(class_id=obj.id)
        ser=SimpleStudentSerializer(queryset,many=True)
        return ser.data
