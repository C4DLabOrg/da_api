
from rest_framework import serializers
from oosc.zone.models import Zone

class ZoneSerializer(serializers.ModelSerializer):
    subcounty_name=serializers.SerializerMethodField()
    county_name=serializers.SerializerMethodField()
    class Meta:
        model=Zone
        fields=('__all__')

    def get_county_name(self,obj):
        if obj.county:
            return obj.county.county_name


    def get_subcounty_name(self,obj):
        if obj.subcounty:
            return obj.subcounty.name