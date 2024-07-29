from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('training_plans/', views.TrainingPlansListView.as_view(), name='training_plans'),
    path('training_plan/<uuid:pk>/', views.TrainingPlanDetailView.as_view(), name='training_plan_detail'),
    path('add_exercise/<uuid:pk>/', views.add_exercise, name='add_exercise'),
    path('delete_exercise/<uuid:pk>/<str:exercise_name>/', views.delete_exercise, name='delete_exercise'),
]