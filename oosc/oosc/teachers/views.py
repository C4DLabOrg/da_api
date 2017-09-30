from django.shortcuts import render
from rest_framework import status,generics
# Create your views here.
from rest_framework import serializers
from rest_framework.exceptions import APIException
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from oosc.teachers.models import Teachers
from rest_framework.response import Response
from django.contrib.auth.models import User,Group
from oosc.teachers.serializers import TeacherSerializer,TeacherAllSerializer,Passwordserializer,ForgotPAsswordSerializer
from oosc.partner.models import Partner
from oosc.partner.serializers import PartnerSerializer
from permission import IsHeadteacherOrAdmin
from rest_framework.views import APIView
from django_filters.rest_framework import FilterSet,DjangoFilterBackend
import django_filters
from django.db.models import Q

from oosc.stream.models import Stream


class TeacherFilter(FilterSet):
    name=django_filters.CharFilter(name="name",label="name",method="filter_name")
    class Meta:
        model=Teachers
        fields=['name','tsc_no','qualifications','school','active','gender','headteacher']
    def filter_name(self,queryset,name,value):
        return queryset.filter(Q(fstname__icontains=value) | Q(lstname__icontains=value))

class StandardresultPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 1000
    page_size_query_param = 'page_size'

class ListTeachers(generics.ListAPIView):
    queryset = Teachers.objects.all()
    serializer_class = TeacherSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class=TeacherFilter
    pagination_class = StandardresultPagination

    def get_queryset(self):
        return Teachers.objects.filter(active=True)

def str2bool(v):
  if type(v) is bool:return v
  return v.lower() in ("yes", "true", "t", "1")

class StreamSerializer(serializers.Serializer):
    headteacher=serializers.BooleanField()
    classes=serializers.ListField( allow_null=True, child=serializers.IntegerField(),error_messages={'required':"The techear should be assigned atlest one class"})
    def validate_classes(self,value):
       hd=str2bool(self.initial_data.get("headteacher"))
       ##print(hd,value)
       if hd:
           return value
       if value is None:
           raise serializers.ValidationError("Classes required")
       sts=list(Stream.objects.filter(id__in=value).values_list("id",flat=True))
       print (sts)
       if(len(sts) <1):raise serializers.ValidationError("Enter Valid stream ids for your school")
       return sts


    # def validate_headteacher(self, value):
    #     if value == False:
    #         raise serializers.ValidationError("Must be a headteacher")
    #     return value


class ListCreateTeachers(APIView):
    permission_classes = (IsHeadteacherOrAdmin,)
    def get(self,request,format=None):
        teach=Teachers.objects.filter(user=self.request.user.id)
        if(len(teach) > 0):
            teachers=TeacherAllSerializer(teach[0])
            return Response(data=teachers.data,status=status.HTTP_200_OK)
        else:
            return Response(data={"error":"Not a teacher"},status=status.HTTP_404_NOT_FOUND)

    def post(self,request,format=None):
        #data=request.data['user']
        details=request.data
        details["details"]["cleanings"]=0
        cls = StreamSerializer(data=details["details"])
        cls.is_valid(raise_exception=True)
        # ##print(cls.validated_data)
        ##Update the details array
        teacher_classes=cls.validated_data.get("classes")
        details["details"]["classes"]=teacher_classes
        # ##print(details["details"])
        # details["details"]["user"] = 272
        # details["details"]["school"] = 62956
        # serializer = TeacherSerializer(data=details['details'])
        # serializer.is_valid(raise_exception=True)
        # serializer.save(class_teachers=teacher_classes)
        # return Response("OK")
        #Create a user for the teacher with a default password 'p@ssw0rd'
        usr=User()
        try:
            # us=list(User.objects.filter(username=details['username']))
            # if len(us)>0:
            #     usr=us[0]
            # else:
            usr=User.objects.create_user(username=details['username'],password='admin')
        except Exception as inst:
            usr.delete()
            return Response(data=inst,status=status.HTTP_400_BAD_REQUEST)

        #add the user to teachers group

        g=Group.objects.get(name="teachers")
        g.user_set.add(usr)

        #set the created user to link to teacher profile with the created id
        details["details"]["user"]=usr.id
        # details["details"]["headteacher"]=False

        #serialieze the teacher details
        serializer=TeacherSerializer(data=details['details'])
        if(serializer.is_valid()):
            #Create the teacher
            dev = serializer.save(class_teachers=teacher_classes)
            ser = TeacherSerializer(dev)
            return Response(ser.data,status=status.HTTP_201_CREATED)
        else:
            usr.delete()
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    #What the post method expects in the request body
    def options(self,request,format=None):
        return Response({"username":"Teachers Username",
                         "details":{"phone_no":"2547..",
                                    "teacher_type":"either TSC for(Tsc) or BRD for(Board)",
                                    "birthday":"yyyy-mm-dd",
                                    "gender":"either ML or FM",
                                    "tsc_no":"tsc no",
                                    "bom_no":"bom number",
                                    "headteacher":"True or False",
                                    "qualifications":"either COL for (college) or UNI for (university)",
                                    "subjects":["ids","of","subjects","required","integers"],
                                    "classes":["ids","of","streams"],
                                    "school":"school id",
                                    "date_started_teaching":"yyyy-mm-dd",
                                    "joined_current_school":"yyyy-mm-dd"
                                    }
                         })

class NonDeleteteacher (APIException):
    status_code = 400
    default_detail = 'You cannot delete this teacher'
    default_code = 'service_unavailable'

class RetrieveUpdateTeacher(generics.RetrieveUpdateDestroyAPIView):
    queryset = Teachers.objects.all()
    serializer_class = TeacherSerializer

    def delete(self, request, *args, **kwargs):
        object=self.get_object()
        if object.non_delete:raise NonDeleteteacher
        usr=User.objects.get(id=object.user_id)
        usr.delete()
        return Response("", status=status.HTTP_204_NO_CONTENT)




class ChangePassword(generics.UpdateAPIView):
    serializer_class =Passwordserializer
    model=User
    permission_classes = (IsAuthenticated,)
    def get_object(self):
        obj=self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object=self.get_object()
        serializer=self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response("Success.", status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasssword(generics.UpdateAPIView):
    model=User
    serializer_class = ForgotPAsswordSerializer
    def get_object(self,username):
        obj=User.objects.get(username=username)
        return obj

    def update(self, request, *args, **kwargs):
        serializer=self.get_serializer(data=self.request.data)
        if serializer.is_valid():
            self.object=self.get_object(serializer.data.get("username"))
            if(self.object):
                self.object.set_password("123")
                self.object.save()
                return Response("Success.", status=status.HTTP_200_OK)
            else:
                return Response("User Not Found",status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetUserType(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self,request,format=None):
        #return Response("hello")
        user=request.user
        partner=Partner.objects.filter(user=user)
        teacher=Teachers.objects.filter(user=user)
        if(user.is_superuser):
            return Response({"type":"admin"})
        elif(partner.exists()):
            partner=partner[0]
            return Response({"type":"partner","info":PartnerSerializer(partner).data})
        elif(teacher.exists()):
            teacher=teacher[0]
            if teacher.headteacher:
                return Response({"type":"teacher","info":TeacherAllSerializer(teacher).data})
            return Response({"details":"You must be an admin of the school"},status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"type":"unknown"},status=status.HTTP_401_UNAUTHORIZED)


class PingServer(APIView):
    def get(self,request,format=None):
        return Response("")






