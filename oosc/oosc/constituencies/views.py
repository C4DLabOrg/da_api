from rest_framework import generics
# Create your views here.
from oosc.mylib.common import StandardresultPagination, MyDjangoFilterBackend
from oosc.zone.models import Zone
from oosc.zone.serializers import ZoneSerializer

class ListCreateCounstituency(generics.ListCreateAPIView):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    pagination_class = StandardresultPagination
    filter_backends = (MyDjangoFilterBackend,)



