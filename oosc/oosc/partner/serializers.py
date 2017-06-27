from rest_framework import serializers
from oosc.partner.models import Partner


class PartnerSerializer(serializers.ModelSerializer):
    email=serializers.SerializerMethodField()
    class Meta:
        model=Partner
        fields=('id','name','email','phone')
    def get_email(self,obj):
        return obj.user.username

class SavePartnerSerializer(serializers.ModelSerializer):
    email=serializers.SerializerMethodField()
    class Meta:
        model=Partner
        fields=('id','name','user','email','phone')
    def get_email(self,obj):
        return obj.user.username

class PostPartnerSerializer(serializers.Serializer):
    name=serializers.CharField(max_length=50)
    email=serializers.CharField(max_length=50)
    phone=serializers.CharField(max_length=50)
    user=serializers.IntegerField(required=False)

    def validate_name(self, value):
        partners=Partner.objects.filter(name=value)
        if(partners.exists()):
            raise serializers.ValidationError("Partner name already taken")
        return value