# Generated by Django 5.0.6 on 2024-08-18 08:16

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("parents", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="child",
            name="user",
        ),
    ]
