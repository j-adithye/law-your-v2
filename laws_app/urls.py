from rest_framework.routers import DefaultRouter
from .views import SectionViewset, ContextSections
from django.urls import path,include

router = DefaultRouter()

router.register('sections',SectionViewset)

urlpatterns = [
    path('',include(router.urls)),
    path('search/',ContextSections.as_view(), name = 'retrieve')
]

