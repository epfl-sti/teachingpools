# Generated by Django 3.0.2 on 2020-01-17 12:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0017_auto_20191211_1000'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timereport',
            name='MAN_term',
        ),
        migrations.RemoveField(
            model_name='timereport',
            name='MAN_year',
        ),
        migrations.RemoveField(
            model_name='timereport',
            name='master_thesis_term',
        ),
        migrations.RemoveField(
            model_name='timereport',
            name='master_thesis_year',
        ),
        migrations.RemoveField(
            model_name='timereport',
            name='other_job_term',
        ),
        migrations.RemoveField(
            model_name='timereport',
            name='other_job_year',
        ),
        migrations.RemoveField(
            model_name='timereport',
            name='semester_project_term',
        ),
        migrations.RemoveField(
            model_name='timereport',
            name='semester_project_year',
        ),
    ]