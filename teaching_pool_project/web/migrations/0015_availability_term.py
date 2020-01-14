# Generated by Django 2.2.7 on 2019-12-06 13:05

from django.db import migrations, models


def populate_availability_term(apps, schema_editor):
    """
    Populates the 'term' field of 'Availabilities' already in the database
    """
    Availability = apps.get_model('web', 'availability')
    for row in Availability.objects.filter(term__isnull=True):
        row.term = 'winter'
        row.save()


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0014_applications_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='availability',
            name='term',
            field=models.CharField(choices=[('winter', 'winter'), ('summer', 'summer')], max_length=255, null=True),
        ),
        migrations.RunPython(populate_availability_term, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='availability',
            name='term',
            field=models.CharField(choices=[('winter', 'winter'), ('summer', 'summer')], max_length=255)
        )
    ]