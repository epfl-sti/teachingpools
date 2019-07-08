import io

from django.conf import settings
from django.core.management.base import BaseCommand

from web.models import Topic


class Command(BaseCommand):
    def handle(self, **options):
        # Load the list of topics
        with open(settings.LIST_OF_TOPICS,'r') as file:
            topics = file.readlines()
            topics = [topic.strip() for topic in topics]

        for topic in topics:
            topic_obj, created = Topic.objects.get_or_create(name=topic)
            if created:
                topic_obj.name = topic
            topic_obj.save()
