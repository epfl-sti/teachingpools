from web.models import Config, Course


def run():
    config = Config.objects.first()
    year = config.current_year
    term = config.current_term

    all_courses = Course.objects.filter(year=year, term=term).all()
    for course in all_courses:
        print("{year} - {term} - {code} - {subject}".format(year=year, term=term, code=course.code, subject=course.subject))

    # first, we want to work on the number of approved TAs
        latest_approved_TA_request = course.numberoftaupdaterequest_set.filter(status__iexact="approved").order_by('-closedAt').first()

        if latest_approved_TA_request:
            if course.approvedNumberOfTAs == latest_approved_TA_request.requestedNumberOfTAs:
                # print("OK -> number of approved TAs equals the latest approved request")
                pass
            else:
                print("\tKO -> number of approved TAs mismatch ({} vs {} approved)".format(course.approvedNumberOfTAs, latest_approved_TA_request.requestedNumberOfTAs))

        # if there is no request for TA, then we default to the calculated one
        else:
            if course.approvedNumberOfTAs is not None and course.approvedNumberOfTAs > 0:
                print("\tKO -> number of approved TAs mismatch (should be 0)")
                course.approvedNumberOfTAs = 0
                course.save()
                print("fixed")

        # time to look at the applications for this course
        applications_accepted = 0
        applications_rejected = 0
        applications_withdrawn = 0
        applications_pending = 0
        applications_received = 0

        applications = course.applications_set.all()
        for application in applications:
            applications_received += 1

            if application.status == 'Hired':
                applications_accepted += 1
            elif application.status == 'Rejected':
                applications_rejected += 1
            elif application.status == 'Withdrawn':
                applications_withdrawn += 1
            elif application.status == "Pending":
                applications_pending += 1

        if course.applications_received != applications_received:
            print("\tKO -> applications received ({} vs {} applications received)".format(course.applications_received, applications_received))
            course.applications_received = applications_received
            course.save()

        if applications_accepted != course.applications_accepted:
            print("\tKO -> applications accepted ({} vs {} applications accepted)".format(course.applications_accepted, applications_accepted))
            course.applications_accepted = applications_accepted
            course.save()

        if applications_rejected != course.applications_rejected:
            print("\tKO -> applications rejected ({} vs {} applications rejected)".format(course.applications_rejected, applications_rejected))
            course.applications_rejected = applications_rejected
            course.save()

        if applications_withdrawn != course.applications_withdrawn:
            print("\tKO -> applications withdrawn ({} vs {} applications withdrawn)".format(applications_withdrawn, course.applications_withdrawn))
            course.applications_withdrawn = applications_withdrawn
            course.save()
