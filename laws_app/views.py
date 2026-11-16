from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import SectionSerializer
from .models import Section
from .search import retrieve

# Create your views here.
class SectionViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    
class ContextSections(APIView):
    def get(self, request):
        question = request.query_params.get("q")
        limit = request.query_params.get('limit')

        results = retrieve(question,limit=int(limit))
        
        data = [
            {'Section': result.number,
            'Title': result.title}
            for result in results
        ]
        
        return Response(data)