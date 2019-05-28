from rest_framework import serializers

from oosc.partner.models import Partner




class AttendanceImportErrorSerializer(serializers.Serializer):
    row_number=serializers.IntegerField()
    error_message=serializers.CharField()

class AttendanceImportResultsSerializer(serializers.Serializer):
    errors=serializers.ListField(child=AttendanceImportErrorSerializer())
    total_success=serializers.IntegerField()
    total_fails=serializers.IntegerField()
    total_duplicates=serializers.IntegerField()
    success_percentage=serializers.SerializerMethodField()

    def get_success_percentage(self,obj):
        total=obj.total_fails+obj.total_success+obj.total_duplicates
        if total ==0:
            return "0%"
        return str(int(((obj.total_success+obj.total_duplicates)/float(total))*100))+"%"

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

