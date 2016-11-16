from rest_framework import generics
# Create your views here.
from oosc.constituencies.models import Constituencies
from oosc.constituencies.serializers import ConstituenciesSerializer

class ListCreateCounstituency(generics.ListCreateAPIView):
    queryset = Constituencies.objects.all()
    serializer_class = ConstituenciesSerializer



