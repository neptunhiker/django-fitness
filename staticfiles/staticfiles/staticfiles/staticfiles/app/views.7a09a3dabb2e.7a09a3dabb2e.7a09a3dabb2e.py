from datetime import datetime, timedelta
from typing import Any

from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView, ListView, DetailView
from django.http import HttpResponseBadRequest, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views import View
from django.template.loader import render_to_string


from .import models, forms
# Create your views here.
class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['training_schedules'] = models.TrainingSchedule.objects.filter(athlete=self.request.user)
        else:
            context['training_schedules'] = models.TrainingSchedule.objects.none()
        return context
    
    
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
        if training_plan.exercises is not None:
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

class TrainingScheduleDetailView(DetailView):
    model = models.TrainingSchedule
    template_name = 'training_schedule_detail.html'
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        training_schedule = get_object_or_404(models.TrainingSchedule, pk=self.kwargs['pk'])
        date = datetime.today().date()
        target_vs_actual_absolute = training_schedule.get_target_vs_actual_absolute(date)
        target_vs_actual_cumulative = training_schedule.get_target_vs_actual_cumulative(date)
        context['target_vs_actual_absolute'] = target_vs_actual_absolute
        context['target_vs_actual_cumulative'] = target_vs_actual_cumulative
        return context
    
    
class GetTrainingScheduleAnalysisView(View):
    def get(self, request, *args, **kwargs):
        training_schedule = models.TrainingSchedule.objects.get(pk=kwargs['pk'])
        selected_date = request.GET.get('date')
        if selected_date is None:
            # Handle the error, for example by returning an HTTP 400 response
            return HttpResponseBadRequest("Missing 'date' parameter")
        
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()

        # Get the activities for the selected date
        target_vs_actual_absolute = training_schedule.get_target_vs_actual_absolute(selected_date)
        target_vs_actual_cumulative = training_schedule.get_target_vs_actual_cumulative(selected_date)
        
        # Format the target activities into HTML
        target_activities_html = render_to_string('target_vs_actual.html', {'target_vs_actual_absolute': target_vs_actual_absolute, 'target_vs_actual_cumulative': target_vs_actual_cumulative})

        # Return the target activities as an HTML response
        return HttpResponse(target_activities_html)
    

class RecordStrengthActivityView(TemplateView):
    template_name = 'strength_activity_create.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = forms.RecordStrengthActivityForm()
        context["training_schedule"] = models.TrainingSchedule.objects.get(pk=self.kwargs["pk"])
        return context

    def post(self, request, **kwargs):
        form = forms.RecordStrengthActivityForm(self.request.POST)
        if form.is_valid():
            training_schedule = models.TrainingSchedule.objects.get(pk=self.kwargs['pk'])
            athlete = self.request.user
            exercise = form.cleaned_data['exercise']
            date = form.cleaned_data['date']
            repetitions = form.cleaned_data['repetitions']
            weight = form.cleaned_data['weight']

            activity = models.StrengthActivity.objects.create(
                exercise=exercise, 
                date=date, 
                athlete=athlete, 
                reps=repetitions, 
                weight=weight
            )
            training_schedule.record_activity(activity)

            return redirect('training_schedule_detail', pk=training_schedule.pk)

        return self.render_to_response(self.get_context_data(form=form))
    
class RecordIsometricActivityView(TemplateView):
    template_name = 'isometric_activity_create.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = forms.RecordIsometricActivityForm()
        context["training_schedule"] = models.TrainingSchedule.objects.get(pk=self.kwargs["pk"])
        return context

    def post(self, request, **kwargs):
        form = forms.RecordIsometricActivityForm(self.request.POST)
        if form.is_valid():
            training_schedule = models.TrainingSchedule.objects.get(pk=self.kwargs['pk'])
            athlete = self.request.user
            exercise = form.cleaned_data['exercise']
            date = form.cleaned_data['date']
            duration = form.cleaned_data['duration']

            activity = models.IsometricActivity.objects.create(
                exercise=exercise, 
                date=date, 
                athlete=athlete, 
                duration=duration, 
            )
            training_schedule.record_activity(activity)

            return redirect('training_schedule_detail', pk=training_schedule.pk)

        return self.render_to_response(self.get_context_data(form=form))
    

class RecordCardioActivityView(TemplateView):
    template_name = 'cardio_activity_create.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = forms.RecordCardioActivityForm()
        context["training_schedule"] = models.TrainingSchedule.objects.get(pk=self.kwargs["pk"])
        return context

    def post(self, request, **kwargs):
        form = forms.RecordCardioActivityForm(self.request.POST)
        if form.is_valid():
            training_schedule = models.TrainingSchedule.objects.get(pk=self.kwargs['pk'])
            athlete = self.request.user
            exercise = form.cleaned_data['exercise']
            date = form.cleaned_data['date']
            duration = form.cleaned_data['duration']

            activity = models.CardioActivity.objects.create(
                exercise=exercise, 
                date=date, 
                athlete=athlete, 
                duration=duration, 
            )
            training_schedule.record_activity(activity)

            return redirect('training_schedule_detail', pk=training_schedule.pk)

        return self.render_to_response(self.get_context_data(form=form))