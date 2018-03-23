from django_subquery.expressions import Subquery
from rest_framework import serializers

from oosc.mylib.common import MyCustomException
from oosc.promotions.models import PromoteStream, PromoteSchool
#
# class PromotionsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Promotions
#         fields = ('promotion_id', 'student_id', 'promotions')



class PromoteStreamSerializer(serializers.ModelSerializer):
    next_class_name=serializers.SerializerMethodField()
    class Meta:
        model=PromoteStream
        fields=('id','prev_class','next_class','completed','modified','next_class_name')

    def get_next_class_name(self,obj):
        return obj.next_class.class_name


class PromoteSchoolSerializer(serializers.ModelSerializer):
    stream_promotions=PromoteStreamSerializer(many=True)

    class Meta:
        model=PromoteSchool
        fields=('id','created','modified','stream_promotions','school','completed','year')
        read_only_fields=('graduates_class',)
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=PromoteSchool.objects.all(),
                fields=('school', 'year'),
                message="Promotions already done for this school."
            )
        ]


    def create(self, validated_data):
        stream_promotions=validated_data.pop("stream_promotions")
        promote_school=PromoteSchool.objects.create(**validated_data)
        streamproms=[]
        for streamprom in stream_promotions:
            p=PromoteStream(next_class=streamprom["next_class"],prev_class=streamprom["prev_class"],promote_school_id=promote_school.id)
            streamproms.append(p)
        PromoteStream.objects.bulk_create(streamproms)
        return promote_school
        # return promote_school

    def update(self, instance, validated_data):

        if instance.completed:raise MyCustomException("Promotion already completed. Undo to update.",404)
        stream_promotions = validated_data.pop("stream_promotions")
        stream_proms=PromoteStream.objects.filter(promote_school_id=instance.id)
        PromoteSchool.objects.filter(id=instance.id).update(**validated_data)
        for streamp in stream_promotions:
            PromoteStream.objects.filter(id__in= Subquery(stream_proms.values("id")) ).filter(prev_class=streamp["prev_class"]).update(**streamp)

        return instance


# class PostPromoteSchoolSerializer(serializers.Serializer):
#     promote_streams=serializers.ListField(child=PromoteStreamSerializer())
#     promote_school=PromoteSchoolSerializer()