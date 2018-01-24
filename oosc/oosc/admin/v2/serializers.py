from django.contrib.auth.models import User
from rest_framework import serializers

class ResetPasswordSerializer(serializers.Serializer):
    username=serializers.CharField(max_length=50)
    password=serializers.CharField(required=False,max_length=50,write_only=True)


    def validate_username(self,value):
        if User.objects.filter(username=value).exists():
            return value
        raise serializers.ValidationError("Phone/Emiscode account does not exist.")