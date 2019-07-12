from web.models import Course, Person

def run():
	users_to_keep = [
		'veronique.michaud@epfl.ch',
		'roberto.zoia@epfl.ch',
		'olivier.martin@epfl.ch',
		'roland.loge@epfl.ch',
		'francois.gallaire@epfl.ch',
		'jean-philippe.thiran@epfl.ch',
		'yves.leterrier@epfl.ch',
		'pierre-etienne.bourban@epfl.ch',
		'david.atienza@epfl.ch',
		'enzo.bomal@epfl.ch',
		'enrico.casamenti@epfl.ch',
		'sherif.fahmy@epfl.ch',
		'eliott.guenat@epfl.ch',
		'alain.takabayashi@epfl.ch',
		'eirini.kakkava@epfl.ch',
		'vivek.ramachandran@epfl.ch',
		'guillaume.broggi@epfl.ch',
		'emmanuel.jaep@epfl.ch',
		]

	for person in Person.objects.all():
		if person.email.lower() not in users_to_keep:
			person.email = "noreply@epfl.ch"
			person.save()

	for course in Course.objects.filter(approvedNumberOfTAs__isnull=True, calculatedNumberOfTAs__isnull=False, calculatedNumberOfTAs__gt=0):
		course.approvedNumberOfTAs = course.calculatedNumberOfTAs
		course.save()
