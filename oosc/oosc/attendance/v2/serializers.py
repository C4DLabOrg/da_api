from rest_framework import serializers

from oosc.partner.models import Partner


class ExportAttendanceSerializer(serializers.Serializer):
    month=serializers.IntegerField(max_value=12,min_value=1)
    year=serializers.IntegerField(max_value=2020,min_value=2010)
    partner=serializers.IntegerField()

    def validate_partner(self,value):
        if value == None:
            pass
        if Partner.objects.filter(id=value).exists():
            return value
        raise serializers.ValidationError("Partner does not exist.")

