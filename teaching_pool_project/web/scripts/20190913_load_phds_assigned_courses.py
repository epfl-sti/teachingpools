from web.models import Config, Course, Applications, Person
import pandas as pd
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone


def process_row(row):
	code = row['Code']
	subject = row['Subject']
	sciper = row['Sciper']

	try:
		config = Config.objects.first()
		year = config.current_year
		term = config.current_term
		course = Course.objects.get(code__iexact=code, subject__iexact=subject, year=year, term=term)
	except ObjectDoesNotExist:
		print ("course not found", code, subject)

	try:
		applicant = Person.objects.get(sciper=sciper)
	except ObjectDoesNotExist:
		print("User does not exist", sciper)

	# Do not try to use the Applications.objects.get_or_create unless you want mails to get sent...
	try:
		application = Applications.objects.get(applicant=applicant, course=course)
	except:
		application = Applications()

	application.course = course
	application.applicant = applicant
	application.source = "system"
	application.status = "Hired"
	application.closedAt = timezone.now()
	application.decisionReason = "TA duty assigned by section"
	application.save()
	print(code, subject, sciper, "-> done")


def run():
	config = Config.objects.first()
	year = config.current_year
	term = config.current_term
	df = pd.read_excel(settings.EXCEL_LIST_OF_ASSIGNMENTS)
	df.apply(lambda row: process_row(row), axis=1)
