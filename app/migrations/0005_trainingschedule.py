# Generated by Django 5.0.7 on 2024-07-30 09:21

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0004_alter_exercise_secondary_muscle_focus"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="TrainingSchedule",
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
                (
                    "notes",
                    models.TextField(
                        blank=True,
                        help_text="Add any additional notes for the training schedule if you wish to do so",
                        null=True,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                (
                    "start_date",
                    models.DateField(help_text="Start date of the training schedule"),
                ),
                (
                    "duration",
                    models.PositiveIntegerField(help_text="Duration in weeks"),
                ),
                (
                    "train_on_mondays",
                    models.BooleanField(
                        default=False,
                        help_text="Decide whether Monday shall be a training day",
                    ),
                ),
                (
                    "train_on_tuesdays",
                    models.BooleanField(
                        default=False,
                        help_text="Decide whether Tuesday shall be a training day",
                    ),
                ),
                (
                    "train_on_wednesdays",
                    models.BooleanField(
                        default=False,
                        help_text="Decide whether Wednesday shall be a training day",
                    ),
                ),
                (
                    "train_on_thursdays",
                    models.BooleanField(
                        default=False,
                        help_text="Decide whether Thursday shall be a training day",
                    ),
                ),
                (
                    "train_on_fridays",
                    models.BooleanField(
                        default=False,
                        help_text="Decide whether Friday shall be a training day",
                    ),
                ),
                (
                    "train_on_saturdays",
                    models.BooleanField(
                        default=False,
                        help_text="Decide whether Saturday shall be a training day",
                    ),
                ),
                (
                    "train_on_sundays",
                    models.BooleanField(
                        default=False,
                        help_text="Decide whether Sunday shall be a training day",
                    ),
                ),
                ("target_activities", models.JSONField(blank=True, null=True)),
                ("actual_activities", models.JSONField(blank=True, null=True)),
                (
                    "athlete",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "training_plan",
                    models.ForeignKey(
                        help_text="Select the training plan to be used for the training schedule",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="app.trainingplan",
                    ),
                ),
            ],
            options={
                "ordering": ["start_date"],
            },
        ),
    ]
