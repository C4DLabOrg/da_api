from rest_framework import serializers
from oosc.schools.models import Schools


class PostSchoolSerializer(serializers.ModelSerializer):

    class Meta:
        model=Schools
        fields=('id','school_code', 'school_name','level','status', 'latitude','longitude', 'emis_code', 'zone', 'source_of_water',
        'headteacher','phone_no')
class SchoolsSerializer(serializers.ModelSerializer):
    #headteacher_name=serializers.SerializerMethodField()
    geo_coordinates=serializers.SerializerMethodField()
    zone=serializers.SerializerMethodField()
    county=serializers.SerializerMethodField()
    class Meta:
        model = Schools
        fields = ('id','school_code', 'school_name','level','county','status', 'geo_coordinates', 'emis_code', 'zone', 'source_of_water',
        'headteacher','phone_no')

    def get_geo_coordinates(self,obj):
        return {"lat":obj.latitude,"lng":obj.longitude}

    def get_subcounty(self,obj):
        return obj.zone.subcounty.name
    def get_zone(self,obj):
        return obj.zone.name
    def get_county(self,obj):
        return obj.zone.county.county_name
    # def get_headteacher_name(self,obj):
    #     return obj.headteacher.username