# Generated by Django 2.2.2 on 2019-06-17 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0005_auto_20190617_2124'),
    ]

    operations = [
        migrations.AddField(
            model_name='teaching',
            name='isLeadTeacher',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='teaching',
            name='role',
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
    ]