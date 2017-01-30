from rest_framework import generics
# Create your views here.
from oosc.zone.models import Zone
from oosc.zone.serializers import ZoneSerializer

class ListCreateCounstituency(generics.ListCreateAPIView):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer



