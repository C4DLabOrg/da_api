from rest_framework import serializers
from oosc.attendance.models import Attendance

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ('id','student','date','status','cause_of_absence','_class')
