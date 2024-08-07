# Generated by Django 5.0.7 on 2024-07-31 06:49

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0006_alter_trainingschedule_options"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Activity",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("date", models.DateField()),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                (
                    "athlete",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Executed by",
                    ),
                ),
                (
                    "exercise",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="app.exercise"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CardioActivity",
            fields=[
                (
                    "activity_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="app.activity",
                    ),
                ),
                ("duration", models.IntegerField(help_text="Duration in seconds")),
            ],
            options={
                "ordering": ["-date", "exercise"],
            },
            bases=("app.activity",),
        ),
        migrations.CreateModel(
            name="IsometricActivity",
            fields=[
                (
                    "activity_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="app.activity",
                    ),
                ),
                ("duration", models.IntegerField(help_text="Duration in seconds")),
            ],
            options={
                "ordering": ["-date", "exercise"],
            },
            bases=("app.activity",),
        ),
        migrations.CreateModel(
            name="StrengthActivity",
            fields=[
                (
                    "activity_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="app.activity",
                    ),
                ),
                ("reps", models.IntegerField()),
                ("weight", models.IntegerField()),
            ],
            options={
                "ordering": ["-date", "exercise"],
            },
            bases=("app.activity",),
        ),
    ]
