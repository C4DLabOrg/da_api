from rest_framework import serializers
from oosc.teachers.models import Teachers
from django.contrib.auth.models import User
from oosc.subjects.models import Subjects
from oosc.subjects.serializers import SubjectSerializer
from oosc.classes.models import Classes
from oosc.classes.serializers import StudentsClassSerializer
from oosc.reason.models import Reason
from oosc.reason.serializers import ReasonSerializer


class TeacherSerializer(serializers.ModelSerializer):
    school_name=serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    class Meta:
        model = Teachers
        fields = ('id','user','name','lstname','active','fstname','phone_no','teacher_type','birthday','gender','tsc_no','bom_no','headteacher','qualifications','subjects','school','date_started_teaching','joined_current_school','school_name')
    def get_school_name(self,obj):
        if not obj.school:
            return None
        return obj.school.school_name
    def get_name(self,obj):
        return obj.fstname+" "+obj.lstname

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=('username','id')

class TeacherAllSerializer(serializers.ModelSerializer):
    subjects=serializers.SerializerMethodField()
    classes=serializers.SerializerMethodField()
    profile=serializers.SerializerMethodField()
    reasons=serializers.SerializerMethodField()
    teachers=serializers.SerializerMethodField()
    class Meta:
        model = Teachers
        fields = ('id','profile','subjects','classes','reasons','teachers')

    def get_subjects(self,obj):
        queryset=Subjects.objects.filter(id__in=obj.subjects.all())
        ser=SubjectSerializer(queryset,many=True)
        return ser.data

    def get_classes(self,obj):
        if obj.headteacher:
            queryset=Classes.objects.filter(school =obj.school).order_by("class_name",)
            print("Headteacher")
        else:
            print("Normal Teacher") 
            queryset = Classes.objects.filter(teacher=obj.id).order_by("class_name", )
        ser=StudentsClassSerializer(queryset,many=True)
        return ser.data
    def get_profile(self,obj):
        return TeacherSerializer(obj).data
    def get_reasons(self,obj):
        return ReasonSerializer(Reason.objects.all(),many=True).data
    def get_teachers(self,obj):
        if not obj.headteacher:
            return None
        return TeacherSerializer(Teachers.objects.filter(school=obj.school,active=True),many=True).data

class Passwordserializer(serializers.Serializer):
    old_password=serializers.CharField(required=True)
    new_password=serializers.CharField(required=True)

class ForgotPAsswordSerializer(serializers.Serializer):

    def validate_username(self,value):
        if not value:
            raise serializers.ValidationError("This field required.")
        if not User.objects.filter(username=value).exists():
            raise serializers.ValidationError("User not Found")
        return value

    username=serializers.CharField(required=True)

