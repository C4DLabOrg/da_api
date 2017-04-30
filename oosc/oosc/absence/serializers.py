
from oosc.absence.models import Absence
from rest_framework import serializers
from oosc.students.serializers import SimpleStudentSerializer
from datetime import datetime

class AbsenceSerializer(serializers.ModelSerializer):
    class Meta:
        model=Absence
        fields=('id','student','_class','reasons','date_from','date_to','status')


class DetailedAbsenceserializer(serializers.ModelSerializer):
    student=serializers.SerializerMethodField()
    days=serializers.SerializerMethodField()
    class Meta:
        model=Absence
        fields=('id','student','_class','days','status','student','reasons','date_from','date_to')

    def get_student(self,obj):
        return SimpleStudentSerializer(obj.student).data
    def get_days(self,obj):
        if obj.date_to:
            return (obj.date_to-obj.date_from).days
        return (datetime.now().date()-obj.date_from).days