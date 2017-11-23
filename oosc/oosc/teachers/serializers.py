from django.db.models import Count
from rest_framework import serializers

from oosc.promotions.models import PromoteSchool
from oosc.promotions.serializers import PromoteSchoolSerializer
from oosc.teachers.models import Teachers
from django.contrib.auth.models import User
from oosc.subjects.models import Subjects
from oosc.subjects.serializers import SubjectSerializer
from oosc.stream.models import Stream
from oosc.stream.serializers import StudentsStreamSerializer
from oosc.reason.models import Reason
from oosc.reason.serializers import ReasonSerializer
from oosc.students.models import Students


class TeacherSerializer(serializers.ModelSerializer):
    school_name=serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    # classes=serializers.SerializerMethodField(read_only=True)
    classes = serializers.PrimaryKeyRelatedField( source="class_teachers", many=True,queryset=Stream.objects.all())
    class Meta:
        model = Teachers
        fields = ('id','user','name','lstname','classes','non_delete','active','fstname','phone_no','teacher_type','birthday','gender','tsc_no','bom_no','headteacher','qualifications','school','date_started_teaching','joined_current_school','school_name')
    def get_school_name(self,obj):
        if not obj.school:
            return None
        return obj.school.school_name

    def get_name(self,obj):
        return obj.fstname+" "+obj.lstname

    # def get_classes(self,obj):
    #     return obj.class_teachers.all()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=('username','id')


class TeacherAllSerializer(serializers.ModelSerializer):
    # subjects=serializers.SerializerMethodField()
    classes=serializers.SerializerMethodField()
    profile=serializers.SerializerMethodField()
    reasons=serializers.SerializerMethodField()
    teachers=serializers.SerializerMethodField()
    schoolinfo=serializers.SerializerMethodField()
    promotion=serializers.SerializerMethodField()
    class Meta:
        model = Teachers
        fields = ('id','profile','classes','reasons','non_delete','promotion','teachers','schoolinfo')

    # def get_subjects(self,obj):
    #     queryset=Subjects.objects.filter(id__in=obj.subjects.all())
    #     ser=SubjectSerializer(queryset,many=True)
    #     return ser.data

    def get_classes(self,obj):
        if obj.headteacher:
            queryset=Stream.objects.filter(school =obj.school).order_by("_class" )
        else:
            queryset = obj.class_teachers.all()
        ser=StudentsStreamSerializer(queryset, many=True)
        return ser.data
    def get_profile(self,obj):
        return TeacherSerializer(obj).data

    def get_schoolinfo(self,obj):
        if obj.headteacher:
            students=Students.objects.filter(active=True,class_id__school=obj.school).values("is_oosc","gender").annotate(count=Count("gender"))
            studs=self.format_students_number(students)

            streams=Stream.objects.filter(school=obj.school).count()
            teachers=Teachers.objects.filter(school=obj.school).count()
            return {"teachers":teachers,"classes":streams,"students":studs["total"],"studs":studs}
        else:return {"teachers":[],"classes":[],"students":[],"studs":[]}

    def format_students_number(self,students):
        re={}
        re["total"]=0
        re["total_males"]=0
        re["total_females"]=0
        for d in students:
            re[self.return_name(d["gender"],d["is_oosc"])]=d["count"]
            re["total"]+=d["count"]
            if d["gender"]=="M":re["total_males"]+=d["count"]
            else:re["total_females"]+=d["count"]
        return re

    def return_name(self,gender,is_oosc):
        g="males" if gender=="M" else "females"
        oosc="old" if is_oosc==False else "enrolled"
        return "%s_%s"%(oosc,g)


    def get_reasons(self,obj):
        return ReasonSerializer(Reason.objects.all(),many=True).data

    def get_promotion(self,obj):
        return PromoteSchoolSerializer(PromoteSchool.objects.filter(school=obj.school).last()).data

    def get_teachers(self,obj):
        if not obj.headteacher:
            return []
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

