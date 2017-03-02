from rest_framework import serializers
from oosc.students.models import Students

class StudentsSerializer(serializers.ModelSerializer):
    student_name=serializers.SerializerMethodField()
    class_name=serializers.SerializerMethodField()
    school_name=serializers.SerializerMethodField()
    class Meta:
        model = Students
        fields = ('student_id','date_enrolled', 'emis_code','last_attendance','class_name','school_name','total_absents','student_name', 'fstname','midname','lstname','date_of_birth', 'admission_no', 'class_id',
        'gender', 'previous_class', 'mode_of_transport','time_to_school', 'stay_with', 'household',
        'meals_per_day', 'not_in_school_before', 'emis_code_histories')
    def get_student_name(self,obj):
        return obj.fstname+" "+obj.lstname
    def get_class_name(self,obj):
        return obj.class_id.class_name
    def get_school_name(self,obj):
        return obj.class_id.school.school_name



class SimpleStudentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    class Meta:
        model=Students
        fields=('id','student_id','student_name','gender','date_enrolled', 'emis_code','last_attendance','total_absents', 'fstname','midname','lstname')

    def get_student_name(self, obj):
        return obj.fstname + " " + obj.lstname
