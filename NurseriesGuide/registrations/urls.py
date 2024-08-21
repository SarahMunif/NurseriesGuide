from django.urls import path
from . import views


app_name = "registrations"



urlpatterns = [
    path('create/', views.registration_create, name='registration_create'),

    path('<int:pk>/update-status/', views.registration_update_status, name='registration_update_status'),
    path('registration/add/subscription/<int:nursery_id>/', views.add_subscription, name='add_subscription'),
    
    path('delete/registration/<int:registration_id>/', views.delete_registration, name='delete_registration'),

    path('add/review/<int:nursery_id>/', views.add_review, name='add_review'),

    ]