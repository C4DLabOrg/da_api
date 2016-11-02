from rest_framework import serializers
from oosc.constituencies.models import Constituencies
from rest_framework import serializers
class ConstituenciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Constituencies
        fields = ('constituency','county_id')
