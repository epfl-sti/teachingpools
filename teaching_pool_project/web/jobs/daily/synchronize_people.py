import logging

from django.conf import settings
from django_extensions.management.jobs import DailyJob
from web.helpers import people_sync

logger = logging.getLogger(__name__)


class Job(DailyJob):
    help = "Synchronize accounts between LDAP and the local DB"

    def execute(self):
        people_sync.synchronize_people()

