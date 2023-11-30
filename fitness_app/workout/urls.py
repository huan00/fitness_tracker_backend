from django.urls import path, include
from . import views
from .views import create_workout

urlpatterns = [
  path('saveworkout', views.create_workout, name='create_workout')
]
