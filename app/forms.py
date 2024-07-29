from django import forms
from .import models


class AddExerciseForm(forms.Form):
    exercise = forms.ModelChoiceField(queryset=models.Exercise.objects.all(), help_text='Choose an exercise for the Training Plan')
    starting_repetitions = forms.IntegerField(label='Starting repetitions', initial=12, min_value=1, help_text='Starting repetitions per training day')
    repetition_progression_per_week = forms.IntegerField(label='Repetition progression', initial=0, min_value=0, help_text='How many repetitions to add per week')
    starting_weight = forms.DecimalField(label='Starting weight', initial=0, min_value=0, help_text='Starting weight in kgs')
    weight_progression_per_week = forms.DecimalField(label='Weight progression', initial=0, min_value=0, help_text='How much weight in kgs to add per week')