from rest_framework import serializers
from subjects.models import Subjects

class StudentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subjects
        fields = ('subject_name')
