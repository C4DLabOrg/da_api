from rest_framework import serializers
from oosc.students.models import Students

class StudentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Students
        fields = ('student_id', 'emis_code','total_absents', 'student_name','date_of_birth', 'admission_no', 'class_id',
        'gender', 'previous_class', 'mode_of_transport','time_to_school', 'stay_with', 'household',
        'meals_per_day', 'not_in_school_before', 'emis_code_histories')

class SimpleStudentSerializer(serializers.ModelSerializer):

    class Meta:
        model=Students
        fields=('id','student_id', 'emis_code','total_absents', 'student_name')
