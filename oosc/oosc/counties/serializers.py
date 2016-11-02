from rest_framework import serializers
from oosc.counties.models import Counties
from rest_framework import serializers
class CountiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Counties
        fields = ('county_name','id')
        
