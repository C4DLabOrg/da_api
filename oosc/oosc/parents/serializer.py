from rest_framework import serializers
from parents.models import Parents

class ParentsSerializer(serializer.ModelSerializer):
    class Meta:
        model = Parents
        fields = ('parents_name','phone_no','student_id')
