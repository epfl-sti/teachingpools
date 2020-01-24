from django import template

register = template.Library()


@register.filter(name="get_total_hours")
def get_total_hours(timereporting_entry):
    return int(timereporting_entry.master_thesis_supervision_hours or 0) + \
        int(timereporting_entry.class_teaching_preparation_hours or 0) + \
        int(timereporting_entry.class_teaching_teaching_hours or 0) + \
        int(timereporting_entry.class_teaching_practical_work_hours or 0) + \
        int(timereporting_entry.semester_project_supervision_hours or 0) + \
        int(timereporting_entry.other_job_hours or 0) + \
        int(timereporting_entry.MAN_hours or 0)
