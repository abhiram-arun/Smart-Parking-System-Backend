from django.urls import path
from . import views

urlpatterns = [
    path('enter/', views.vehicle_entry),
    path('exit/', views.vehicle_exit),
    path('logs/', views.vehicle_logs),
]