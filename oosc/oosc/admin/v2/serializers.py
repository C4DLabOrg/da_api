from django.contrib.auth.models import User
from rest_framework import serializers

from oosc.schools.models import Schools


class ResetPasswordSerializer(serializers.Serializer):
    username=serializers.CharField(max_length=50)
    password=serializers.CharField(required=True,max_length=50,write_only=True)


    def validate_username(self,value):
        if User.objects.filter(username=value).exists():
            return value
        raise serializers.ValidationError("Phone/Emiscode account does not exist.")

class SchoolEmiscodesSerializer(serializers.Serializer):
    emis_codes=serializers.ListField(child=serializers.IntegerField())
    def validate_emis_codes(self,value):
        unverified_emis_codes=set(value)
        verified_emis_codes=list(Schools.objects.filter(emis_code__in=unverified_emis_codes).values_list("emis_code",flat=True))
        # print (verified_emis_codes)
        if len(verified_emis_codes) < 1:
            raise serializers.ValidationError("No schools were found.")
        return verified_emis_codes

