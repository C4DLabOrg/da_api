from rest_framework import serializers
from counties.models import Counties

class CountiesSerializer(serializer.ModelSerializer):
    class Meta:
        model = Counties
        fields = ('county_name')
        
