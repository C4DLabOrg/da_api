
from rest_framework import serializers
from oosc.zone.models import Zone

class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model=Zone
        fields=('id','county','subcounty','name')