# Generated by Django 2.2.2 on 2019-06-17 20:18

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0008_numberoftaupdaterequest'),
    ]

    operations = [
        migrations.CreateModel(
            name='Applications',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('openedAt', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.CharField(default='Pending', max_length=255)),
                ('closedAt', models.DateTimeField(blank=True, default=None, null=True)),
                ('decisionReason', models.TextField(blank=True, default=None, null=True)),
                ('applicant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applicant', to='web.Person')),
                ('closedBy', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='web.Person')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.Course')),
            ],
        ),
    ]
