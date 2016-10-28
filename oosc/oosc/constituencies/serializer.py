from rest_framework import serializers
from counties.models import Constituencies

class ConstituenciesSerializer(serializer.ModelSerializer):
    class Meta:
        model = Constituencies
        fields = ('constituency','county_id')
