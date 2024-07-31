import datetime 
from django.db.models import JSONField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

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
        ('Full Body', 'Full Body'),
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
    secondary_muscle_focus = models.ForeignKey(Muscle, related_name='secondary_exercises', on_delete=models.CASCADE, blank=True, null=True)
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
    
    
class Activity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    date = models.DateField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    athlete = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Executed by"
        )
    
class StrengthActivity(Activity):
    reps = models.IntegerField()
    weight = models.IntegerField()
    
    class Meta:
        ordering = ['-date', 'exercise']
        verbose_name_plural = 'Strength activities'
        
    def __str__(self):
        return f"Strength activity for {self.exercise.name} - {self.reps} reps - {self.weight} kg"
    
class IsometricActivity(Activity):
    duration = models.IntegerField(help_text="Duration in seconds")
    
    class Meta:
        ordering = ['-date', 'exercise']
        verbose_name_plural = 'Isometric activities'
        
    def __str__(self):
        return f"Isometric activity for {self.exercise.name} - {self.duration} seconds hold"
    
class CardioActivity(Activity):
    duration = models.IntegerField(help_text="Duration in seconds")
    
    class Meta:
        ordering = ['-date', 'exercise']
        verbose_name_plural = 'Cardio activities'
        
    def __str__(self):
        return f"Cardio activity for {self.exercise.name} - {self.duration} seconds"

class TrainingPlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Created by"
        )
    exercises = JSONField(blank=True, null=True)
    
    class Meta:
        ordering = ['name']
        
    def get_absolute_url(self):
        return reverse('training_plan_detail', args=[str(self.id)])
    
    def __str__(self):
        return self.name
    
class TrainingSchedule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    athlete = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notes = models.TextField(blank=True, null=True, help_text="Add any additional notes for the training schedule if you wish to do so")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    training_plan = models.ForeignKey(TrainingPlan, on_delete=models.CASCADE, help_text="Select the training plan to be used for the training schedule")
    start_date = models.DateField(help_text="Start date of the training schedule")
    duration = models.PositiveIntegerField(help_text="Duration in weeks")
    CHOICES = (
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),    
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),    
        ('Sunday', 'Sunday'),
    )
    train_on_mondays = models.BooleanField(default=False, help_text="Decide whether Monday shall be a training day")
    train_on_tuesdays = models.BooleanField(default=False, help_text="Decide whether Tuesday shall be a training day")
    train_on_wednesdays = models.BooleanField(default=False, help_text="Decide whether Wednesday shall be a training day")
    train_on_thursdays = models.BooleanField(default=False, help_text="Decide whether Thursday shall be a training day")
    train_on_fridays = models.BooleanField(default=False, help_text="Decide whether Friday shall be a training day")
    train_on_saturdays = models.BooleanField(default=False, help_text="Decide whether Saturday shall be a training day")
    train_on_sundays = models.BooleanField(default=False, help_text="Decide whether Sunday shall be a training day")
    target_activities = JSONField(blank=True, null=True)
    actual_activities = JSONField(blank=True, null=True)
    
    def get_training_week(self, date:datetime.date) -> int:
        """Function that returns the training week number based on the start date and the given date"""
        if date < self.start_date or date > self.end_date:
            raise ValueError("Given date is outside the training schedule")
        
        delta = date - self.start_date
        return delta.days // 7 + 1
    
    def _add_target_activities(self):
        """Function that adds the target activities for the entire duration of the training schedule based on the exercises of the underlying training plan"""
        if self.target_activities is None:
            self.target_activities = dict()
            
        delta = datetime.timedelta(days=1)
        current_date = self.start_date
        while current_date <= self.end_date:
            if not self.is_training_day(current_date):
                # not a training day
                target = dict()
                for exercise_name in self.training_plan.exercises.keys():
                    target[exercise_name] = [0, 0]
                self.target_activities[current_date.isoformat()] = target
            else:
                # training day
                target = dict()
                training_week = self.get_training_week(current_date)
                for exercise_name, values in self.training_plan.exercises.items():
                    starting_reps = values[0]
                    repetition_progression_per_week = values[1]
                    target_reps = starting_reps + (training_week - 1) * repetition_progression_per_week
                    starting_weight = values[2]
                    weight_progression_per_week = values[3]
                    target_weight = starting_weight + (training_week - 1) * weight_progression_per_week
                    target[exercise_name] = [target_reps, target_weight]
                self.target_activities[current_date.isoformat()] = target
            
            current_date += delta
        
        self.save()
        
    def get_target_activity_absolute(self, date:datetime.date, exercise_name:str) -> list:
        """Function that returns the target repetitions and weight for the given date and exercise"""
        if exercise_name not in self.training_plan.exercises.keys():
            raise ValueError("Given exercise is not part of the training plan")
        
        if date < self.start_date or date > self.end_date:
            raise ValueError("Given date is outside the training schedule")
        
        return self.target_activities[date.isoformat()][exercise_name]
    
    def get_target_repetitions_cumulative(self, date:datetime.date, exercise_name:str) -> list:
        """Function that returns the target repetitions for the given date and exercise"""
        if exercise_name not in self.training_plan.exercises.keys():
            raise ValueError("Given exercise is not part of the training plan")
        
        if date < self.start_date or date > self.end_date:
            raise ValueError("Given date is outside the training schedule")
        
        reps = 0
        for target_date in self.target_activities.keys():
            target_date = datetime.date.fromisoformat(target_date)
            if target_date <= date:
                reps += self.get_target_activity_absolute(target_date, exercise_name)[0]
            
        return reps
    
    def get_all_target_activities(self, date:datetime.date) -> dict:
        """Function that returns the target activities for the given date"""
        if date < self.start_date or date > self.end_date:
            raise ValueError("Given date is outside the training schedule")
        
        target_activities = dict()
        for exercise_name in self.training_plan.exercises.keys():
            cumulative_target_repetitions = self.get_target_repetitions_cumulative(date, exercise_name)
            target_weight = self.get_target_activity_absolute(date, exercise_name)[1]
            target_activities[exercise_name] = [cumulative_target_repetitions, target_weight]
        
        return target_activities
    
    def get_training_days(self):
        """Get a list of boolean values for each day of the week depending on whether it is a training day or not"""
        return [self.train_on_mondays, self.train_on_tuesdays, self.train_on_wednesdays, self.train_on_thursdays, self.train_on_fridays, self.train_on_saturdays, self.train_on_sundays]
    
    def is_training_day(self, date: datetime.date) -> bool:
        """Function that checks whether the given date is a training day or not"""
        weekday = date.weekday()
        if date < self.start_date or date > self.end_date:
            return False
        
        if not self.get_training_days()[weekday]:
            return False

        return True
    
    def record_activity(self, activity: Activity):
        """Function that records the actual activity"""
        if self.athlete != activity.athlete:
            raise ValueError("The athlete who performed the activity does not match the athlete of the training schedule")
        
        date = activity.date
        if date < self.start_date or date > self.end_date:
            raise ValueError("Given date is outside the training schedule")

        exercise_name = activity.exercise.name
        if isinstance(activity, StrengthActivity):
            reps_or_duration = float(activity.reps)
            weight = float(activity.weight)
        elif isinstance(activity, CardioActivity) or isinstance(activity, IsometricActivity):
            reps_or_duration = float(activity.duration)
            weight = 0.0
        else:
            raise ValueError("Given activity is not a strength, cardio or isometric activity")

        self.actual_activities = self.actual_activities or {}

        date_key = date.isoformat()
        self.actual_activities.setdefault(date_key, {})
        self.actual_activities[date_key][exercise_name] = [reps_or_duration, weight]

        self.save()
        
        # to be continued: write a view and template that allows the user to record an activity. The view should change immediately to that date such that the user can see the actual vs the target activities for that date on a cumulative scale but also on an absolute scale. Before you start, sketch out on paper on how the template shall look like.
    
    @property
    def end_date(self):
        return self.start_date + datetime.timedelta(days=self.duration * 7)
    
    def get_absolute_url(self):
        return reverse('training_schedule_detail', args=[str(self.id)])
    
    
    class Meta:
        ordering = ['-start_date']
        
    def __str__(self):
        return f"Training Schedule based on '{self.training_plan.name}' - {self.start_date}"
    
# This method will be called after a TrainingSchedule instance is saved
@receiver(post_save, sender=TrainingSchedule)
def add_target_activities(sender, instance, created, **kwargs):
    if created:
        instance._add_target_activities()