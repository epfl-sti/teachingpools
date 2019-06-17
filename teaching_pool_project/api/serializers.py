from rest_framework import serializers
from web.models import Person, Course, Teaching


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class TeachingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teaching
        fields = '__all__'
