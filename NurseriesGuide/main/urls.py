from django.urls import path
from . import views


app_name = "main"



urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about_us, name='about_us'),
    path('staff/dashboard/',views.staff_dashboard,name="staff_dashboard"),
    path('admin-dashboard/',views.admin_dashboard,name="admin_dashboard"),
    path('contact/', views.contact_view, name="contact_view"),
    path('reviews/', views.add_review, name="add_review"),
    path('terms-of-use/', views.terms_of_use, name="terms_of_use"),
    

]
