from rest_framework import serializers
from attendance.models import Attendance

class AttendanceSerializer(serializer.ModelSerializer):
    class Meta:
        model = Constituencies
        fields = ('student_id','date','status','cause_of_absence','class_id')
