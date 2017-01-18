
from oosc.absence.models import Absence
from rest_framework import serializers
from oosc.students.serializers import SimpleStudentSerializer

class AbsenceSerializer(serializers.ModelSerializer):
    class Meta:
        model=Absence
        fields=('id','student','reasons','date_from','date_to','status')


class DetailedAbsenceserializer(serializers.ModelSerializer):
    student=serializers.SerializerMethodField()
    days=serializers.SerializerMethodField()
    class Meta:
        model=Absence
        fields=('id','student','days','status','student','reasons','date_from','date_to')

    def get_student(self,obj):
        return SimpleStudentSerializer(obj.student).data
    def get_days(self,obj):
        dayte=obj.date_to-obj.date_from
        return dayte.days