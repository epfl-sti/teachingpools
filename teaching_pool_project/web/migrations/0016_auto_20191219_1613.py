# Generated by Django 3.0 on 2019-12-19 15:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0015_availability_term'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='availability',
            unique_together={('year', 'term', 'person')},
        ),
    ]
