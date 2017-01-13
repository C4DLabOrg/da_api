from django.shortcuts import render
from rest_framework import status
# Create your views here.
from oosc.teachers.models import Teachers
from oosc.teachers.serializers import TeacherSerializer,UserSerializer
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User,Group
from oosc.teachers.serializers import UserSerializer,TeacherSerializer,TeacherAllSerializer
from permission import IsHeadteacherOrAdmin

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
        #Create a user for the teacher with a default password 'p@ssw0rd'
        try:
            usr=User.objects.create_user(username=details['username'],password='p@ssw0rd')
        except Exception as inst:
            usr.delete()
            return Response(data=inst,status=status.HTTP_400_BAD_REQUEST)

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
                                    "school":"school id",
                                    "date_started_teaching":"yyyy-mm-dd",
                                    "joined_current_school":"yyyy-mm-dd"
                                    }
                         })





