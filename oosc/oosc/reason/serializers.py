from oosc.reason.models import Reason

from rest_framework import serializers
class ReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model=Reason
        fields=('id','name')
