from rest_framework import serializers
from oosc.schools.models import Schools

class SchoolsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schools
        fields = ('school_code', 'school_name', 'geo_cordinates', 'emis_code', 'constituency', 'source_of_water',
        'headteacher','phone_no')
