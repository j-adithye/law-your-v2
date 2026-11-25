from rest_framework import serializers
from .models import Section


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['number','title','body','illustrations','explanations','exceptions']
        
        
        
class AskRequestSerializer(serializers.Serializer):
    question = serializers.CharField()


class AskResponseSerializer(serializers.Serializer):
    answer = serializers.CharField()
    citations = serializers.ListField(child=serializers.IntegerField())
    found = serializers.BooleanField()
    disclaimer = 'iam an ai assistant and can make mistakes this is not legal advice'