from django import forms
from .import models


class AddExerciseForm(forms.Form):
    exercise = forms.ModelChoiceField(queryset=models.Exercise.objects.all(), help_text='Choose an exercise to add to the Training Plan')
    starting_repetitions = forms.IntegerField(label='Starting repetitions/duration', initial=12, min_value=1, help_text='Starting repetitions or duration in seconds per training day')
    repetition_progression_per_week = forms.IntegerField(label='Repetition/Duration progression', initial=0, min_value=0, help_text='How many repetitions or seconds to add per week')
    starting_weight = forms.DecimalField(label='Starting weight', initial=0, min_value=0, help_text='Starting weight in kgs')
    weight_progression_per_week = forms.DecimalField(label='Weight progression', initial=0, min_value=0, help_text='How much weight in kgs to add per week')



class RecordStrengthActivityForm(forms.Form):
    exercise = forms.ModelChoiceField(queryset=models.Exercise.objects.filter(type="Strength"))
    date = forms.DateField()
    repetitions = forms.IntegerField(min_value=0)
    weight = forms.DecimalField(min_value=0)
    
class RecordIsometricActivityForm(forms.Form):
    exercise = forms.ModelChoiceField(queryset=models.Exercise.objects.filter(type="Isometric"))
    date = forms.DateField()
    duration = forms.IntegerField(min_value=0, help_text='Duration in seconds')
    
class RecordCardioActivityForm(forms.Form):
    exercise = forms.ModelChoiceField(queryset=models.Exercise.objects.filter(type="Cardio"))
    date = forms.DateField()
    duration = forms.IntegerField(min_value=0, help_text='Duration in seconds')