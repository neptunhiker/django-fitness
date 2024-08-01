from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('training_plans/', views.TrainingPlansListView.as_view(), name='training_plans'),
    path('training_plan/<uuid:pk>/', views.TrainingPlanDetailView.as_view(), name='training_plan_detail'),
    path('add_exercise/<uuid:pk>/', views.add_exercise, name='add_exercise'),
    path('delete_exercise/<uuid:pk>/<str:exercise_name>/', views.delete_exercise, name='delete_exercise'),
    path('training_schedule/<uuid:pk>/', views.TrainingScheduleDetailView.as_view(), name='training_schedule_detail'),
    path('get-target-activities/<uuid:pk>/', views.GetTrainingScheduleAnalysisView.as_view(), name='get-target-activities'),
    path('record_strength_activity/<uuid:pk>/', views.RecordStrengthActivityView.as_view(), name='record_strength_activity'),
    path('record_isometric_activity/<uuid:pk>/', views.RecordIsometricActivityView.as_view(), name='record_isometric_activity'),
    path('record_cardio_activity/<uuid:pk>/', views.RecordCardioActivityView.as_view(), name='record_cardio_activity'),
    path('exercise_detail/<uuid:pk>/', views.ExerciseDetailView.as_view(), name='exercise_detail'),
    path('training_plan_create', views.TrainingPlanCreateView.as_view(), name='create_training_plan'),
    path('training_schedule_create', views.TrainingScheduleCreateView.as_view(), name='create_training_schedule'),
    path('help', views.HelpView.as_view(), name='help'),
    path('create_exercise', views.ExerciseCreateView.as_view(), name='create_exercise'),
    path('exercise_list', views.ExerciseListView.as_view(), name='exercise_list'),
]