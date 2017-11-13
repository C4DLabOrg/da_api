from rest_framework import serializers


from oosc.promotions.models import PromoteStream, PromoteSchool
#
# class PromotionsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Promotions
#         fields = ('promotion_id', 'student_id', 'promotions')





class PromoteStreamSerializer(serializers.ModelSerializer):
    class Meta:
        model=PromoteStream
        fields=('id','_class','next_class','completed','modified')


class PromoteSchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model=PromoteSchool
        fields=('id','created','modified','school','promotions','completed','year','graduates_class')
