import logging
from datetime import datetime

import html2text
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.timezone import now
from django_extensions.management.jobs import HourlyJob

from web.models import Mail_campaign, Mail_message

logger = logging.getLogger(__name__)


class Job(HourlyJob):
    help = "Send pending email messages"

    def execute(self):
        logger.info("processing mail campaigns to be sent")

        campaigns = Mail_campaign.objects.filter(
            status__in=["pending", "in-progress"], do_not_send_before__lte = datetime.now()
        ).all()
        logger.debug("{} campaigns".format(len(campaigns)))

        for campaign in campaigns:
            for message in campaign.mail_message_set.all():
                if message.status != "sent" and message.retry_count < 4:
                    self.send_message(message)

            logger.debug("processing stats of the campaign")
            # time to deal with the stats of the campaign
            total_messages = campaign.mail_message_set.count()
            pending_messages = campaign.mail_message_set.filter(
                status="pending"
            ).count()
            sent_messages = campaign.mail_message_set.filter(status="sent").count()
            error_messages = campaign.mail_message_set.filter(
                retry_count__gte=4
            ).count()
            processed_messages = sent_messages + error_messages

            if processed_messages == total_messages:
                if error_messages != 0:
                    campaign.status = "finished with errors"
                else:
                    campaign.status = "successfully finished"
            elif processed_messages > 0:
                campaign.status = "in-progress"
            else:
                campaign.status = "pending"

            campaign.save()

    def send_message(self, message):
        logger.info("sending message")
        logger.debug("to: {}".format(message.to))

        # build the HTML message
        message_content = "<!DOCTYPE html><html><head></head><body>{}</body></html>".format(
            message.message
        )

        # create the text version of the message
        logger.debug("converting message from  HTML to TXT")
        h = html2text.HTML2Text()
        text_message_content = h.handle(message_content)

        # build the recipient list
        tos = list()
        tos.append(message.to)

        # send the message
        try:
            logger.debug("sending")
            msg = EmailMultiAlternatives(
                subject=message.subject,
                body=text_message_content,
                from_email="noreply@epfl.ch",
                to=tos,
            )
            msg.attach_alternative(message_content, "text/html")
            msg.send()

            message.status = "sent"
            message.error_message = None
            message.sent_at = now()
            message.save()
        except Exception as ex:
            logger.exception("unable to send message", exc_info=True)
            logger.error(ex)
            message.status = "error"
            message.error_message = ex
            message.retry_count += 1
            message.save()
