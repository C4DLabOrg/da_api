from rest_framework import serializers
from oosc.subjects.models import Subjects

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subjects
        fields = ('id','subject_name')
