from django.urls import path
from . import views


app_name = "main"



urlpatterns = [
    path('', views.home, name='home'),
    path('staff/dashboard/',views.staff_dashboard,name="staff_dashboard"),
    path('admin/dashboard/',views.admin_dashboard,name="admin_dashboard"),

]
