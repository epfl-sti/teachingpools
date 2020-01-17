# Generated by Django 3.0.2 on 2020-01-17 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0019_auto_20200117_1337'),
    ]

    operations = [
        migrations.AddField(
            model_name='timereport',
            name='class_teaching_exam_hours',
            field=models.IntegerField(blank=True, default=None, null=True, verbose_name='Total number of exam supervision and grading hours (over the semester)'),
        ),
    ]
