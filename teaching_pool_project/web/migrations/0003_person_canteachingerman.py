# Generated by Django 2.2.2 on 2019-06-26 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_availability_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='canTeachInGerman',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
    ]
