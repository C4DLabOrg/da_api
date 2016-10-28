from rest_framework import serializers
from teachers.models import Teachers

class TeacherSerializer(serializer.ModelSerializer):
    class Meta:
        model = Teachers
        fields = ('name','phone_no','type','age','gender','tsc_no','bom_no','qualifications','subjects','school_id',
        'date_started_teaching','joined_current_school')
