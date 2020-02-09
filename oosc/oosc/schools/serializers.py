from rest_framework import serializers
from oosc.schools.models import Schools, Term


class PostSchoolSerializer(serializers.ModelSerializer):

    class Meta:
        model=Schools
        fields=('id','school_code','subcounty', 'school_name','partner_conflict','level','status','partners', 'latitude','longitude', 'emis_code', 'zone', 'source_of_water',
        'headteacher','phone_no','partners')

    # def validate_emis_code(self,value):
    #     if Schools.objects.filter(emis_code=value).exists():
    #         raise serializers.ValidationError("Emis code already exists.")
    #     return value

class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model=Term
        fields=("__all__")




class SchoolsSerializer(serializers.ModelSerializer):
    #headteacher_name=serializers.SerializerMethodField()
    geo_coordinates=serializers.SerializerMethodField()
    zone_name=serializers.SerializerMethodField()
    county_name=serializers.SerializerMethodField()
    subcounty_name=serializers.SerializerMethodField()
    class Meta:
        model = Schools
        fields = ('id','school_code','partner_conflict' , 'latitude','longitude', 'school_name','partners','level'
                  ,'county_name',
                    'subcounty_name',
                 'zone_name'
                  ,'status', 'geo_coordinates', 'emis_code'
                  , 'zone',
                 'subcounty'
                  , 'source_of_water',
        'headteacher','phone_no')


    def get_geo_coordinates(self,obj):
        return {"lat":obj.latitude,"lng":obj.longitude}

    def get_subcounty_name(self,obj):
        if obj.zone != None:
            return obj.zone.subcounty.name
        if obj.subcounty:
            return obj.subcounty.name
        return None

    def get_county_name(self,obj):
        if obj.zone != None:
            return obj.zone.subcounty.county.county_name
        if obj.subcounty:
            return obj.subcounty.county.county_name
        return None

    def get_zone_name(self,obj):
        if obj.zone == None:
            return None
        return obj.zone.name

    # def validate_emis_code(self, value):
    #     if Schools.objects.filter(emis_code=value).exists():
    #         raise serializers.ValidationError("Emis code already exists.")
    #     return value
    # def get_headteacher_name(self,obj):
    #     return obj.headteacher.username