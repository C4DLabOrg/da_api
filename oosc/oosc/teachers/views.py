from django.shortcuts import render
from rest_framework import status
# Create your views here.
from oosc.teachers.models import Teachers
from oosc.teachers.serializers import TeacherSerializer,UserSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User,Group
from oosc.teachers.serializers import UserSerializer,TeacherSerializer

class ListCreateTeachers(APIView):
    def get(self,request,format=None):
        teach=Teachers.objects.all();
        teachers=TeacherSerializer(teach,many=True)
        return Response(teachers.data)

    def post(self,request,format=None):
        #data=request.data['user']
        details=request.data

        #Create a user for the teacher with a default password 'p@ssw0rd'
        usr=User.objects.create_user(username=details['username'],password='p@ssw0rd')

        #add the user to teachers group
        g=Group.objects.get(name="teachers")
        g.user_set.add(usr)

        #set the created user to link to teacher profile with the created id
        details["details"]["user"]=usr.id
        details["details"]["headteacher"]=False

        #serialieze the teacher details
        serializer=TeacherSerializer(data=details['details'])
        if(serializer.is_valid()):
            #Create the teacher
            serializer.save()
            return Response(serializer.validated_data,status=status.HTTP_201_CREATED)
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
                                    "school_id":"school_id",
                                    "date_started_teaching":"yyyy-mm-dd",
                                    "joined_current_school":"yyyy-mm-dd"
                                    }
                         })





