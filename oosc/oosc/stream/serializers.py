from rest_framework import serializers
from oosc.stream.models import Stream
from rest_framework import serializers
from oosc.students.models import Students
from oosc.students.serializers import SimpleStudentSerializer
class StreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stream
        fields = ('id','class_name','school','teachers','_class')

class StudentsStreamSerializer(serializers.ModelSerializer):
    students=serializers.SerializerMethodField()
    class Meta:
        model=Stream
        fields=('id','class_name','students','_class','school')

    def get_students(self,obj):
        queryset=Students.objects.filter(class_id=obj.id,active=True)
        ser=SimpleStudentSerializer(queryset,many=True)
        return ser.data
