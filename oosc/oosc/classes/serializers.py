from rest_framework import serializers
from oosc.classes.models import Classes

class ClassesSerializer(serializers.ModelSerializer):
    class Meta:
        model=Classes
        fields=('name','created','modified')
