from rest_framework import serializers
from oosc.students.models import Students
from datetime import timedelta,datetime
import dateutil.parser

class StudentsSerializer(serializers.ModelSerializer):
    student_name=serializers.SerializerMethodField()
    class_name=serializers.SerializerMethodField()
    school_name=serializers.SerializerMethodField()
    short_name=serializers.SerializerMethodField()
    mode_of_transport_display=serializers.SerializerMethodField()
    time_to_school_display=serializers.SerializerMethodField()
    stay_with_display=serializers.SerializerMethodField()
    class Meta:
        model = Students
        fields = ('id','student_id','dropout_reason','guardian_name','mode_of_transport_display','time_to_school_display','stay_with_display','offline_id','short_name','created','is_oosc','modified','guardian_phone','active','date_enrolled', 'emis_code','last_attendance','class_name','school_name','total_absents','student_name', 'fstname','midname','lstname','date_of_birth', 'admission_no', 'class_id',
        'gender', 'previous_class', 'mode_of_transport','time_to_school', 'stay_with', 'household',
        'meals_per_day', 'not_in_school_before', 'emis_code_histories')

    def get_stay_with_display(self,obj):
        return obj.get_stay_with_display()

    def get_time_to_school_display(self,obj):
        return obj.get_time_to_school_display()

    def get_mode_of_transport_display(self, obj):
        return obj.get_mode_of_transport_display()

    def get_short_name(self,obj):
        if obj.lstname:
            return obj.fstname+" "+obj.lstname
        return obj.fstname + " " + obj.midname

    def get_class_name(self,obj):
        if obj.class_id:
            return obj.class_id.class_name
        return None

    def get_school_name(self,obj):
        if not obj.class_id:
            return None
        return obj.class_id.school.school_name

    def get_student_name(self, obj):
        if obj.lstname and obj.midname:
            return obj.fstname+" "+obj.midname+" "+obj.lstname
        elif obj.lstname:
            return obj.fstname+" "+obj.lstname
        return obj.fstname + " " + obj.midname






class SimpleStudentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    short_name = serializers.SerializerMethodField()
    class Meta:
        model=Students
        fields=("__all__")

    def get_short_name(self, obj):
        if obj.lstname:
            return obj.fstname+" "+obj.lstname
        return obj.fstname + " " + obj.midname

    def get_student_name(self, obj):
        if obj.lstname and obj.midname:
            return obj.fstname + " " + obj.midname + " " + obj.lstname
        elif obj.lstname:
            return obj.fstname + " " + obj.lstname
        return obj.fstname + " " + obj.midname
    #nothing
class SimplerStudentSerializer(serializers.Serializer):
   fstname=serializers.CharField(max_length=150,required=False)
   lstname=serializers.CharField(max_length=150,required=False)
   name=serializers.CharField(max_length=150,required=False)
   gender=serializers.CharField(max_length=150,required=False)
   logs=serializers.CharField(max_length=150,required=False)


class ImportErrorSerializer(serializers.Serializer):
    row_number=serializers.IntegerField()
    error_message=serializers.JSONField()
    row_details=serializers.JSONField()

class ImportResultsSerializer(serializers.Serializer):
    errors=serializers.ListField(child=ImportErrorSerializer())
    total_success=serializers.IntegerField()
    total_fails=serializers.IntegerField()
    total_duplicates=serializers.IntegerField()
    success_percentage=serializers.SerializerMethodField()
    def get_success_percentage(self,obj):
        total=obj.total_fails+obj.total_success+obj.total_duplicates
        if total ==0:
            return "0%"
        return str(int(obj.total_success/float(total)*100))+"%"