from django.contrib.auth.models import User
from rest_framework import serializers

from oosc.partner.serializers import SimlePartnerSerializer
from oosc.schools.models import Schools
from oosc.stream.models import Stream
from oosc.zone.serializers import ZoneSerializer


class ResetPasswordSerializer(serializers.Serializer):
    username=serializers.CharField(max_length=50)
    password=serializers.CharField(required=True,max_length=50,write_only=True)


    def validate_username(self,value):
        if User.objects.filter(username=value).exists():
            return value
        raise serializers.ValidationError("Phone/Emiscode account does not exist.")

class SchoolsSerializerV2(serializers.ModelSerializer):
    zone=ZoneSerializer(read_only=True)
    partners=SimlePartnerSerializer(read_only=True,many=True)
    class Meta:
        model=Schools
        fields=("__all__")

class SchoolEmiscodesSerializer(serializers.Serializer):
    emis_codes=serializers.ListField(child=serializers.IntegerField())
    def validate_emis_codes(self,value):
        unverified_emis_codes=set(value)
        verified_emis_codes=list(Schools.objects.filter(emis_code__in=unverified_emis_codes).values_list("emis_code",flat=True))
        # print (verified_emis_codes)
        if len(verified_emis_codes) < 1:
            raise serializers.ValidationError("No schools were found.")
        return verified_emis_codes

class DeleteStreamStudentsSerializer(serializers.Serializer):
    streams=serializers.ListField(child=serializers.IntegerField())

    def validate_streams(self,value):
        unverified_stream_ids=set(value)
        verified_stream_ids=list(Stream.objects.filter(id__in=unverified_stream_ids).values_list("id",flat=True))
        print(verified_stream_ids)
        if len(verified_stream_ids) < 1:
            raise serializers.ValidationError("No valid streams found.")
        return verified_stream_ids