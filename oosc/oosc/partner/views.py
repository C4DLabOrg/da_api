from django.shortcuts import render
from oosc.partner.models import Partner
# Create your views here.
from rest_framework import generics
from django.contrib.auth.models import User, Group
from oosc.partner.serializers import PartnerSerializer, PostPartnerSerializer
from oosc.partner.permissions import IsAdmin

class ListCreatePartner(generics.ListCreateAPIView):
    queryset = Partner.objects.all()
    serializer_class = PostPartnerSerializer
    permission_classes = (IsAdmin,)
    def get_serializer_class(self):
        if self.request.method == "POST":
            return PostPartnerSerializer
        else:
            return PartnerSerializer


    def perform_create(self, serializer):
        username=serializer.validated_data.get("email")
        password=serializer.validated_data.get("password")
        name=serializer.validated_data.get("name")
        user=User.objects.create_user(username=username,
                                      email=username,password=password)
        g, created = Group.objects.get_or_create(name="partners")
        # print (g,created)
        g.user_set.add(user)
        data=serializer.data
        data["user"]=user.id
        partner=PartnerSerializer(data=data)
        if not partner.is_valid():
            raise serializer.ValidationError(str(partner.errors))
        else:
            #
            partner.save()
