from rest_framework import serializers
from web.models import Person, Course, Teaching


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = '__all__'
        read_only_fields = ('sciper',)
