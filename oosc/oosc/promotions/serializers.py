from rest_framework import serializers
from promotions.models import Promotions

class PromotionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotions
        fields = ('promotion_id', 'student_id', 'promotions')
