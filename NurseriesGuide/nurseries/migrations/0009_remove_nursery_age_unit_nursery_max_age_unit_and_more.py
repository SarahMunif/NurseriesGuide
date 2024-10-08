# Generated by Django 5.1 on 2024-08-26 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nurseries', '0008_nursery_age_unit_nursery_max_age_nursery_min_age_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='nursery',
            name='age_unit',
        ),
        migrations.AddField(
            model_name='nursery',
            name='max_age_unit',
            field=models.CharField(choices=[('months', 'أشهر'), ('years', 'سنوات')], default='years', max_length=10),
        ),
        migrations.AddField(
            model_name='nursery',
            name='min_age_unit',
            field=models.CharField(choices=[('months', 'أشهر'), ('years', 'سنوات')], default='years', max_length=10),
        ),
    ]
