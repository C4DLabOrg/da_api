
from oosc.absence.models import Absence
from rest_framework import serializers

class AbsenceSerializer(serializers.ModelSerializer):
    class Meta:
        model=Absence
        fields=('id','student','reasons','date_from','date_to')
