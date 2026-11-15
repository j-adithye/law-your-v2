from rest_framework import viewsets
from .serializers import SectionSerializer
from .models import Section

# Create your views here.
class SectionViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer