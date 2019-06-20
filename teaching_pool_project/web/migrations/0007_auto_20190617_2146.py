# Generated by Django 2.2.2 on 2019-06-17 19:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0006_auto_20190617_2126'),
    ]

    operations = [
        migrations.CreateModel(
            name='Interests',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='taughtInEnglish',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='course',
            name='taughtInFrench',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='person',
            name='canTeachInEnglish',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='person',
            name='canTeachInFrench',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('interestedPersons', models.ManyToManyField(through='web.Interests', to='web.Person')),
            ],
        ),
        migrations.AddField(
            model_name='interests',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.Person'),
        ),
        migrations.AddField(
            model_name='interests',
            name='topic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.Topic'),
        ),
        migrations.CreateModel(
            name='Availability',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.CharField(max_length=9)),
                ('availability', models.CharField(choices=[('Available', 'Available'), ('Unavailable', 'Unavailable')], default='Available', max_length=255)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.Person')),
            ],
        ),
        migrations.AddField(
            model_name='person',
            name='topics',
            field=models.ManyToManyField(through='web.Interests', to='web.Topic'),
        ),
    ]
