# from django.shortcuts import render

# Create your views here.

from rest_framework import generics, permissions
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import PersonSerializer
from web.models import Person


@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
class PersonCreateView(generics.ListCreateAPIView):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
