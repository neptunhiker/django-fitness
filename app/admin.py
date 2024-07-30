from django.contrib import admin

from .import models

admin.site.register(models.Exercise)
admin.site.register(models.Muscle)
admin.site.register(models.Equipment)
admin.site.register(models.TrainingPlan)
admin.site.register(models.TrainingSchedule)
