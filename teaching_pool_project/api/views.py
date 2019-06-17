# from django.shortcuts import render

# Create your views here.

from rest_framework import generics, permissions
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import PersonSerializer, CourseSerializer, TeachingSerializer
from web.models import Person, Course, Teaching


@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
class Persons(generics.ListCreateAPIView):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer


@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
class PersonDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer


@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
class CourseDetailByYearTermCode(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_object(self):
        year = self.kwargs.get('year')
        term = self.kwargs.get('term')
        code = self.kwargs.get('code')
        course = self.queryset.get(year=year, term=term, code=code)
        return course


@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
class CourseDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
class Courses(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
class Teachings(generics.ListCreateAPIView):
    queryset = Teaching.objects.all()
    serializer_class = TeachingSerializer


@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
class TeachingsBySciper(generics.ListCreateAPIView):
    queryset = Teaching.objects.all()
    serializer_class = TeachingSerializer

    def get_queryset(self):
        return self.queryset.filter(person=self.kwargs.get('sciper'))
