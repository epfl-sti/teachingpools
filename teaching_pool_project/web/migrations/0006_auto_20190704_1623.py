# Generated by Django 2.2.2 on 2019-07-04 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0005_auto_20190703_1109'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='topics',
            field=models.ManyToManyField(blank=True, through='web.Interests', to='web.Topic'),
        ),
    ]
