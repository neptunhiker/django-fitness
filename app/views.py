from typing import Any
from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView, ListView, DetailView
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .import models, forms
# Create your views here.
class HomeView(TemplateView):
    template_name = 'home.html'
    
    
class TrainingPlansListView(LoginRequiredMixin, ListView):
    model = models.TrainingPlan
    template_name = 'training_plans_list.html'
    
class TrainingPlanDetailView(LoginRequiredMixin, DetailView):
    model = models.TrainingPlan
    template_name = 'training_plan_detail.html'
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = forms.AddExerciseForm()
        context['exercises'] = models.Exercise.objects.all()
        training_plan = get_object_or_404(models.TrainingPlan, pk=self.kwargs['pk'])
        equipment_list = []
        for exercise_name, values in training_plan.exercises.items():
            exercise = models.Exercise.objects.get(name=exercise_name)
            for equipment in exercise.equipment.all():
                if equipment not in equipment_list:
                    equipment_list.append(equipment.name)
        context['equipment'] = equipment_list
        return context
    

@login_required
def add_exercise(request, pk):
    if request.method == 'POST':
        form = forms.AddExerciseForm(request.POST)
        if form.is_valid():
            exercise = form.cleaned_data['exercise']
            starting_repetitions = form.cleaned_data['starting_repetitions']
            repetition_progression_per_week = form.cleaned_data['repetition_progression_per_week']
            starting_weight = form.cleaned_data['starting_weight']
            weight_progression_per_week = form.cleaned_data['weight_progression_per_week']

            # Get the training plan
            training_plan = models.TrainingPlan.objects.get(pk=pk)
            if training_plan.exercises is None:
                training_plan.exercises = {}
            training_plan.exercises[exercise.name] = [float(starting_repetitions), float(repetition_progression_per_week), float(starting_weight), float(weight_progression_per_week)]
            training_plan.save()
            print("Exercise added successfully")
            training_plan = models.TrainingPlan.objects.get(pk=pk)
            equipment_list = []
            for exercise_name, values in training_plan.exercises.items():
                exercise = models.Exercise.objects.get(name=exercise_name)
                for equipment in exercise.equipment.all():
                    if equipment not in equipment_list:
                        equipment_list.append(equipment.name)
            return render(request, 'snippet_tp_exercises.html', {'form': form, 'trainingplan': training_plan, 'equipment': equipment_list})
        else:
            return JsonResponse({'errors': form.errors}, status=400)
    else:
        form = forms.AddExerciseForm()
    return render(request, 'snippet_tp_exercises.html', {'form': form})

from django.http import HttpResponse

@login_required
def delete_exercise(request, pk, exercise_name):
    if request.method == 'POST':
        training_plan = models.TrainingPlan.objects.get(pk=pk)
        if training_plan.exercises is not None and exercise_name in training_plan.exercises:
            del training_plan.exercises[exercise_name]
            training_plan.save()
        equipment_list = []
        for exercise_name, values in training_plan.exercises.items():
            exercise = models.Exercise.objects.get(name=exercise_name)
            for equipment in exercise.equipment.all():
                if equipment not in equipment_list:
                    equipment_list.append(equipment.name)
          
    return render(request, 'snippet_tp_exercises.html', {'trainingplan': training_plan, 'equipment': equipment_list})