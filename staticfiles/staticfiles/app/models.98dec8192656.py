import calendar
import datetime 
import uuid

from django.db.models import JSONField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

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
        ('Full Body', 'Full Body'),#
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
        
    
    def get_absolute_url(self):
        return reverse('exercise_detail', args=[str(self.id)])
        
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
        """Function that returns the target repetitions/duration and weight for the given date and exercise"""
        if exercise_name not in self.training_plan.exercises.keys():
            return [0, 0]
        
        if date < self.start_date or date > self.end_date:
            raise ValueError("Given date is outside the training schedule")
        
        return self.target_activities[date.isoformat()][exercise_name]
    
    def get_actual_activity_absolute(self, date:datetime.date, exercise_name:str) -> list:
        """Function that returns the actual repetitions/duration and weight for the given date and exercise"""
        
        if self.actual_activities is not None and date.isoformat() in self.actual_activities.keys():
            if exercise_name not in self.actual_activities[date.isoformat()].keys():
                return [0, 0]
            return self.actual_activities[date.isoformat()][exercise_name]
        
        return [0, 0]
    
    def get_target_repetitions_cumulative(self, date:datetime.date, exercise_name:str) -> list:
        """Function that returns the target repetitions for the given date and exercise"""
        if exercise_name not in self.training_plan.exercises.keys():
            return 0

        if date < self.start_date:
            return 0
        
        if date > self.end_date:
            date = self.end_date
        
        reps = 0
        for target_date in self.target_activities.keys():
            target_date = datetime.date.fromisoformat(target_date)
            if target_date <= date:
                reps += self.get_target_activity_absolute(target_date, exercise_name)[0]
            
        return reps
    
    def get_actual_repetitions_cumulative(self, date:datetime.date, exercise_name:str) -> list:
        """Function that returns the actual repetitions for the given date and exercise"""     
                
        if self.actual_activities is None:
            return 0
        
        reps = 0
        for target_date in self.actual_activities.keys():
            target_date = datetime.date.fromisoformat(target_date)
            if target_date <= date:
                reps += self.get_actual_activity_absolute(target_date, exercise_name)[0]
            
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
    
    def get_all_exercises(self) -> list:
        """Get a list of all exercises that are part of the training plan or part of the recorded activities"""
        all_exercises = list(self.training_plan.exercises.keys())
        if self.actual_activities is not None:
            for date, values in self.actual_activities.items():
                for exercise_name in values.keys():
                    if exercise_name not in all_exercises:
                        all_exercises.append(exercise_name)
        return all_exercises
    
    def get_target_vs_actual_absolute(self, date:datetime.date) -> dict:
        """
        Get a dictionary for each exercise that shows the target vs actual activities on the given date
        
        Returns:
            dict: {exercise_name: [[target_repetitions, target_weight], [actual_repetitions, actual_weight], [gap_repetitions, gap_weight]]}
        """
        target_vs_actual = dict()
        all_exercises = self.get_all_exercises()
        
        
        for exercise_name in all_exercises:
            if date < self.start_date or date > self.end_date:
                target = [0, 0]
            else:
                target = self.get_target_activity_absolute(date, exercise_name)  # list[reps/duration, weight]
            actual = self.get_actual_activity_absolute(date, exercise_name)  # list[reps/duration, weight]
            gap = [actual[0] - target[0], actual[1] - target[1]]
            exercise = Exercise.objects.get(name=exercise_name)
            target_vs_actual[exercise] = [target, actual, gap]
        
        return target_vs_actual
    
    def get_target_vs_actual_cumulative(self, date:datetime.date) -> dict:
        """
        Get a dictionary for each exercise that shows the target vs actual cumulative activities up to the given date from the start date of the training schedule
        
        Returns:
            dict: {exercise_name: [target_repetitions, actual_repetitions, gap_repetitions]}
        """
        
        target_vs_actual = dict()
        all_exercises = self.get_all_exercises()
        
        for exercise_name in all_exercises:
            target = self.get_target_repetitions_cumulative(date, exercise_name)  # target reps
            actual = self.get_actual_repetitions_cumulative(date, exercise_name)  # actual reps
            gap = actual - target
            target_vs_actual[exercise_name] = [target, actual, gap]
        
        return target_vs_actual


    def get_training_days(self):
        """Get a list of boolean values for each day of the week depending on whether it is a training day or not"""
        return [self.train_on_mondays, self.train_on_tuesdays, self.train_on_wednesdays, self.train_on_thursdays, self.train_on_fridays, self.train_on_saturdays, self.train_on_sundays]
    
    def get_training_days_as_string(self):
        """Get a string representation of the training days"""
        
        return [calendar.day_name[i] for i, day in enumerate(self.get_training_days()) if day]
    
    def get_number_of_recorded_activities(self):
        """Get the number of recorded activities"""
        if self.actual_activities is None:
            return 0
        
        recorded_activities = 0
        for date, values in self.actual_activities.items():
            for exercise_name in values.keys():
                recorded_activities += 1
        return recorded_activities
    
    def get_unique_exercises_recorded(self) -> list:
        """Get a list of unique exercises that are recorded"""
        if self.actual_activities is None:
            return []
        
        unique_exercises = []
        for date, values in self.actual_activities.items():
            for exercise_name in values.keys():
                if exercise_name not in unique_exercises:
                    unique_exercises.append(exercise_name)
        return unique_exercises
    
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