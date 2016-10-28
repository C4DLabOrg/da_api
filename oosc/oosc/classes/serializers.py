from rest_framework import serializers
from classes.models import Classes

class ClassesSerializer(serializer.ModelSerializer):
    class Meta:
        model = Constituencies
        fields = ('class_name','school_id','teacher_id')
