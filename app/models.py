from django.db import models
import uuid

from src import settings

class Muscle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    CHOICES = (
        ('Chest', 'Chest'),
        ('Back', 'Back'),
        ('Legs', 'Legs'),
        ('Glutes', 'Glutes'),
        ('Arms', 'Arms'),
        ('Shoulders', 'Shoulders'),
        ('Core', 'Core'),
    )
    muscle_group = models.CharField(max_length=150, choices=CHOICES)

    class Meta:
        ordering = ['muscle_group', 'name']
        
    def __str__(self):
        return f"{self.name} ({self.muscle_group})"
    
class Equipment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'equipment'
        
    def __str__(self):
        return self.name
    
class Exercise(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    primary_muscle_focus = models.ForeignKey(Muscle, related_name='primary_exercises', on_delete=models.CASCADE)
    secondary_muscle_focus = models.ForeignKey(Muscle, related_name='secondary_exercises', on_delete=models.CASCADE)
    equipment = models.ManyToManyField(Equipment, blank=True)
    CHOICES = (
        ('Cardio', 'Cardio'),
        ('Strength', 'Strength'),
        ('Isometric', 'Isometric'),
    )
    type = models.CharField(max_length=50, choices=CHOICES)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Created by"
        )

    class Meta:
        ordering = ['type', 'name']
        
    def __str__(self):
        return self.name