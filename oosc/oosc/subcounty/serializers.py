from rest_framework import serializers
from oosc.subcounty.models import SubCounty

class SubCountySerializer(serializers.ModelSerializer):
    class Meta:
        model=SubCounty
        fields=('id','name','county')