# Generated by Django 5.0.7 on 2024-07-31 06:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0007_activity_cardioactivity_isometricactivity_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="strengthactivity",
            options={
                "ordering": ["-date", "exercise"],
                "verbose_name_plural": "Strength activities",
            },
        ),
    ]
