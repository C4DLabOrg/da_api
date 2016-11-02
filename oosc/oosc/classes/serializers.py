from rest_framework import serializers
from oosc.classes.models import Classes
from rest_framework import serializers

class ClassesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classes
        fields = ('class_name','school_id','teacher_id')
