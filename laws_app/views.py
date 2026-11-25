from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import SectionSerializer,AskRequestSerializer, AskResponseSerializer
from .models import Section
from .search import retrieve
from .generation import get_answer, get_context, parse_answer

from drf_spectacular.utils import extend_schema


# Create your views here.
class SectionViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer

class ContextSections(APIView):
    def get(self, request):
        question = request.query_params.get("q")
        limit = request.query_params.get('limit',5)

        results = retrieve(question,top_n=int(limit))
        
        return Response(SectionSerializer(results, many=True).data)

class AskView(APIView):
    @extend_schema(request=AskRequestSerializer, responses=AskResponseSerializer)
    def post(self, request):
        serializer = AskRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.validated_data["question"]
        context = get_context(question=question)
        
        raw = get_answer(question,context)
        result = parse_answer(raw)  # should return the dict: answer, citations, found

        return Response(AskResponseSerializer(result).data)