from datetime import datetime, timedelta
from typing import Any

from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.http import HttpResponseBadRequest, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views import View
from django.template.loader import render_to_string
from django.db.models import Q


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
            
            exercises = dict()
            for exercise_name, values in training_plan.exercises.items():
                exercise = models.Exercise.objects.get(name=exercise_name)
                exercises[exercise] = values
            context['exercises'] = exercises
        
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
            
            exercises = dict()
            for exercise_name, values in training_plan.exercises.items():
                exercise = models.Exercise.objects.get(name=exercise_name)
                exercises[exercise] = values
            
            return render(request, 'snippet_tp_exercises.html', {'form': form, 'trainingplan': training_plan, 'equipment': equipment_list, 'exercises': exercises})
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
                    
        exercises = dict()
        for exercise_name, values in training_plan.exercises.items():
            exercise = models.Exercise.objects.get(name=exercise_name)
            exercises[exercise] = values
          
    return render(request, 'snippet_tp_exercises.html', {'trainingplan': training_plan, 'equipment': equipment_list, 'exercises': exercises})

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
        if selected_date < training_schedule.start_date or selected_date > training_schedule.end_date:
            date_warning = True
        else:
            date_warning = False

        # Get the activities for the selected date
        target_vs_actual_absolute = training_schedule.get_target_vs_actual_absolute(selected_date)
        target_vs_actual_cumulative = training_schedule.get_target_vs_actual_cumulative(selected_date)
        
        # Format the target activities into HTML
        target_activities_html = render_to_string('target_vs_actual.html', {'target_vs_actual_absolute': target_vs_actual_absolute, 'target_vs_actual_cumulative': target_vs_actual_cumulative, 'date': selected_date, "date_warning": date_warning, "training_schedule": training_schedule})

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
    

class ExerciseDetailView(DetailView):
    model = models.Exercise
    template_name = 'exercise_detail.html'
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        q_objects = Q(primary_muscle_focus=self.object.primary_muscle_focus) | Q(secondary_muscle_focus=self.object.primary_muscle_focus)
        if self.object.secondary_muscle_focus is not None:
            q_objects |= Q(primary_muscle_focus=self.object.secondary_muscle_focus) | Q(secondary_muscle_focus=self.object.secondary_muscle_focus)
        similar_exercises = models.Exercise.objects.filter(q_objects).exclude(id=self.object.id)
        similar_exercises = similar_exercises.order_by('name')
        context["similar_exercises"] = similar_exercises
        other_exercises = models.Exercise.objects.exclude(id=self.object.id).exclude(id__in=similar_exercises)
        other_exercises = other_exercises.order_by('name')
        
        context["other_exercises"] = other_exercises
        return context
    

class TrainingPlanCreateView(CreateView):
    model = models.TrainingPlan
    template_name = 'training_plan_create.html'
    success_url = reverse_lazy('training_plans')
    fields = ['name', 'description']
    
    def form_valid(self, form):
        training_plan = form.save(commit=False)
        training_plan.author = self.request.user
        training_plan.save()
        return super().form_valid(form)
    
class TrainingScheduleCreateView(CreateView):
    model = models.TrainingSchedule
    template_name = 'training_schedule_create.html'
    success_url = reverse_lazy('home')
    fields = ['notes', 'training_plan', 'start_date', 'duration', 'train_on_mondays', 'train_on_tuesdays', 'train_on_wednesdays', 'train_on_thursdays', 'train_on_fridays', 'train_on_saturdays', 'train_on_sundays']
    
    def form_valid(self, form):
        training_plan = form.save(commit=False)
        training_plan.athlete = self.request.user
        training_plan.save()
        return super().form_valid(form)
    
    
class HelpView(TemplateView):
    template_name = 'help.html'
    
class ExerciseCreateView(CreateView):
    model = models.Exercise
    template_name = 'exercise_create.html'
    success_url = reverse_lazy('exercise_list')
    fields = ['name', 'description', 'primary_muscle_focus', 'secondary_muscle_focus', 'equipment', 'type']
    
    def form_valid(self, form):
        exercise = form.save(commit=False)
        exercise.author = self.request.user
        exercise.save()
        return super().form_valid(form)
    
class ExerciseListView(ListView):
    model = models.Exercise
    template_name = 'exercise_list.html'
    context_object_name = 'exercises'
    
    def get_queryset(self):
        return models.Exercise.objects.all().order_by('name')