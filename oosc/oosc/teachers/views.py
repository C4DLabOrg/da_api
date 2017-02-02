from django.shortcuts import render
from rest_framework import status,generics
# Create your views here.
from rest_framework.permissions import IsAuthenticated
from oosc.teachers.models import Teachers
from rest_framework.response import Response
from django.contrib.auth.models import User,Group
from oosc.teachers.serializers import TeacherSerializer,TeacherAllSerializer,Passwordserializer,ForgotPAsswordSerializer
from permission import IsHeadteacherOrAdmin
from rest_framework.views import APIView


class ListTeachers(generics.ListAPIView):
    queryset = Teachers.objects.all()
    serializer_class = TeacherSerializer


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
            dev = serializer.save()
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
                                    "school":"school id",
                                    "date_started_teaching":"yyyy-mm-dd",
                                    "joined_current_school":"yyyy-mm-dd"
                                    }
                         })



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






