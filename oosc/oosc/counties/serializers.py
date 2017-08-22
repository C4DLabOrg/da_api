from rest_framework import serializers
from oosc.counties.models import Counties
from rest_framework import serializers

from oosc.subcounty.serializers import SimpleSubCountySerializer


class CountiesSerializer(serializers.ModelSerializer):
    subcounties = SimpleSubCountySerializer(many=True, read_only=True)
    class Meta:
        model = Counties
        fields = ('county_name','id','subcounties')
        
