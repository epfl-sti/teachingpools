from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils.safestring import mark_safe
import logging

logger = logging.getLogger(__name__)

def notify_admins_and_requester(data, template_base, admins_subject, requesters_subject, admins, requesters):
    logger.info("notifying admins and requesters by mail")

    admins_template = '{}_admins'.format(template_base)
    admins_sender = settings.EMAIL_FROM
    admin_recipients = admins
    notify_people(data=data, template=admins_template, subject=admins_subject,
                  sender=admins_sender, recipients=admin_recipients)

    requester_template = '{}_requester'.format(template_base)
    requester_sender = settings.EMAIL_FROM
    requester_recipients = requesters
    notify_people(data=data, template=requester_template, subject=requesters_subject,
                  sender=requester_sender, recipients=requester_recipients)


def notify_people(data={}, template='', subject='', sender='', recipients=list()):
    logger.info("notifying people by mail")
    logger.debug("template: %s", template)
    logger.debug("subject: %s", subject)
    logger.debug("sender: %s", sender)
    logger.debug("recipients: %s", recipients)

    data['ENVIRONMENT_TYPE'] = settings.ENVIRONMENT_TYPE

    mail_subject = settings.EMAIL_SUBJECT_PREFIX + subject
    plaintext = get_template('web/emails/{}.txt'.format(template))
    htmly = get_template('web/emails/{}.html'.format(template))
    text_content = plaintext.render(data)
    htmly_content = htmly.render(data)
    msg = EmailMultiAlternatives(
        subject=mail_subject,
        body=text_content,
        from_email=sender,
        to=recipients)
    msg.attach_alternative(htmly_content, "text/html")
    msg.send()
