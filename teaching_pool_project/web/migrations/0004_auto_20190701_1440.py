# Generated by Django 2.2.2 on 2019-07-01 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0003_person_canteachingerman'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='applications_accepted',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='course',
            name='applications_received',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='course',
            name='applications_rejected',
            field=models.IntegerField(default=0),
        ),
    ]
