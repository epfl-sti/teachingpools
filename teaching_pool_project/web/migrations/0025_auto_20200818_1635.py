# Generated by Django 3.1b1 on 2020-08-18 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0024_course_coursebook_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='first name'),
        ),
    ]