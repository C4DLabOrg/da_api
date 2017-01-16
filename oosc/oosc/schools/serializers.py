from rest_framework import serializers
from oosc.schools.models import Schools

class SchoolsSerializer(serializers.ModelSerializer):
    #headteacher_name=serializers.SerializerMethodField()
    class Meta:
        model = Schools
        fields = ('school_code', 'school_name','level','status', 'geo_cordinates', 'emis_code', 'zone', 'source_of_water',
        'headteacher','phone_no')

    # def get_headteacher_name(self,obj):
    #     return obj.headteacher.username