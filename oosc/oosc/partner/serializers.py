from rest_framework import serializers
from oosc.partner.models import Partner


class PartnerSerializer(serializers.ModelSerializer):
    email=serializers.SerializerMethodField()
    class Meta:
        model=Partner
        fields=('id','name','user','email')
    def get_email(self,obj):
        return obj.user.username


class PostPartnerSerializer(serializers.Serializer):
    name=serializers.CharField(max_length=50)
    email=serializers.CharField(max_length=50)
    password=serializers.CharField(max_length=50,write_only=True)