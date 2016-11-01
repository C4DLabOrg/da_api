from rest_framework import serializers
from oosc.attendance.models import Attendance

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ('student_id','date','status','cause_of_absence','class_id')
