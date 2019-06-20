# Generated by Django 2.2.2 on 2019-06-18 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0013_auto_20190618_0851'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='availability',
            unique_together={('year', 'person')},
        ),
        migrations.AlterIndexTogether(
            name='availability',
            index_together={('year', 'person')},
        ),
        migrations.AddIndex(
            model_name='availability',
            index=models.Index(fields=['year'], name='web_availab_year_e26324_idx'),
        ),
        migrations.AddIndex(
            model_name='availability',
            index=models.Index(fields=['person'], name='web_availab_person__2f5310_idx'),
        ),
    ]