from django.db.models import Case
from django.db.models import IntegerField, Count
from django.db.models import Q
from django.db.models import When
from rest_framework import serializers
from oosc.partner.models import Partner
from oosc.students.models import Students


class PartnerSerializer(serializers.ModelSerializer):
    email=serializers.SerializerMethodField()
    students=serializers.SerializerMethodField()
    # males=serializers.IntegerField(read_only=True,default=0,required=False)
    # total=serializers.IntegerField(read_only=True,default=0,required=False)
    # females=serializers.IntegerField(read_only=True,default=0,required=False)

    class Meta:
        model=Partner
        fields=('id','name','email','phone','test','last_data_upload',
                'students',
                # "males","females",
                # "total"
                )
    def get_email(self,obj):
        return obj.user.username

    def get_students(self,obj):
        sts= list(Students.objects.filter(active=True,class_id__school__partners__id=obj.id).order_by().values("gender","is_oosc").annotate(count=Count("gender")))
        females=self.get_count(sts,"F",is_oosc=True)
        males=self.get_count(sts,"M",is_oosc=True)
        old_females = self.get_count(sts, "F", is_oosc=False)
        old_males = self.get_count(sts, "M", is_oosc=False)
        return {"males":males,"females":females,
                "enrolled_males": males, "enrolled_females": females,
                "old_females":old_females,
                "old_males":old_males,
                "total":males+females+old_females+old_males,"total_enrolled":males+females}

    def get_count(self,list,item,is_oosc):
        obs=[g["count"] for g in list if g["gender"]==item and g["is_oosc"]==is_oosc ]
        if len(obs)>0:return obs[0]
        return 0

class SavePartnerSerializer(serializers.ModelSerializer):
    email=serializers.SerializerMethodField()
    class Meta:
        model=Partner
        fields=('id','name','user','email','phone')
    def get_email(self,obj):
        return obj.user.username

class PostPartnerSerializer(serializers.Serializer):
    name=serializers.CharField(max_length=50)
    email=serializers.CharField(max_length=50)
    phone=serializers.CharField(max_length=50)
    user=serializers.IntegerField(required=False)

    def validate_name(self, value):
        partners=Partner.objects.filter(name=value)
        if(partners.exists()):
            raise serializers.ValidationError("Partner name already taken")
        return value