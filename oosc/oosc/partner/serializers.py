from rest_framework import serializers
from oosc.partner.models import Partner


class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model=Partner
        fields=('id','name','user')


class PostPartnerSerializer(serializers.Serializer):
    name=serializers.CharField(max_length=50)
    email=serializers.CharField(max_length=50)
    password=serializers.CharField(max_length=50,write_only=True)