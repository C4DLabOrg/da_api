from rest_framework import serializers
from oosc.teachers.models import Teachers
from django.contrib.auth.models import User
class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teachers
        fields = ('__all__')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=('username','id')