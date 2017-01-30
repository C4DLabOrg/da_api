from rest_framework import serializers
from oosc.schools.models import Schools

class SchoolsSerializer(serializers.ModelSerializer):
    #headteacher_name=serializers.SerializerMethodField()
    geo_coordinates=serializers.SerializerMethodField()
    class Meta:
        model = Schools
        fields = ('id','school_code', 'school_name','level','status', 'geo_coordinates', 'emis_code', 'zone', 'source_of_water',
        'headteacher','phone_no')

    def get_geo_coordinates(self,obj):
        return {"lat":obj.latitude,"lng":obj.longitude}

    # def get_headteacher_name(self,obj):
    #     return obj.headteacher.username