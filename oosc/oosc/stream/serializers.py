from rest_framework import serializers

from oosc.mylib.common import my_class_name
from oosc.stream.models import Stream
from rest_framework import serializers
from oosc.students.models import Students
from oosc.students.serializers import SimpleStudentSerializer
class StreamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Stream
        fields = ('id','class_name','school','teachers','_class','last_attendance')


    def validate_class_name(self,value):
        cl=self.initial_data
        return my_class_name(cl)



class GetStreamSerializer(serializers.ModelSerializer):
    class_name=serializers.SerializerMethodField()
    class Meta:
        model = Stream
        fields = ('id','class_name','school','teachers','_class','last_attendance')

    def get_class_name(self, obj):
        return my_class_name(obj)






class StudentsStreamSerializer(serializers.ModelSerializer):
    students=serializers.SerializerMethodField()
    class_name = serializers.SerializerMethodField()
    class Meta:
        model=Stream
        fields=('id','class_name','students','_class','school','last_attendance')

    def get_students(self,obj):
        queryset=Students.objects.filter(class_id=obj.id,active=True)
        ser=SimpleStudentSerializer(queryset,many=True)
        return ser.data

    def get_class_name(self,obj):
        return  my_class_name(obj)
