from django.urls import path
from . import views


app_name = "registrations"



urlpatterns = [
    path('create/', views.registration_create, name='registration_create'),
    path('', views.registration_list, name='registration_list'),
    path('<int:pk>/', views.registration_detail, name='registration_detail'),
    path('<int:pk>/update-status/', views.registration_update_status, name='registration_update_status'),
    path('registration/add/subscription/<int:nursery_id>/', views.add_subscription, name='add_subscription'),
    ]