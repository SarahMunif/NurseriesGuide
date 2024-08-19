from django.urls import path
from . import views


app_name = "main"



urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about_us, name='about_us'),
    path('contact/', views.contact_us, name='contact_us'),
    path('staff/dashboard/',views.staff_dashboard,name="staff_dashboard"),
    path('admin-dashboard/',views.admin_dashboard,name="admin_dashboard"),
]
