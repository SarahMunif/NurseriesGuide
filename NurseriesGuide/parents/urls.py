from django.urls import path
from . import views

app_name = "parents"

urlpatterns = [

    path('add/', views.add_child, name="add_child"),
    path('update/', views.update_parent, name="update_parent"),
    path('delete/child/', views.delete_child, name="delete_child"),
    path('update/child/', views.update_child, name="update_child"),
    path('signup/manager/', views.signup_manager, name="signup_manager"),
    path('signup/parent/', views.signup_parent, name="signup_parent"),
    # path('<user_name>/', views.parent_profile, name="parent_profile"),
    path('signin/', views.signin, name="signin"),
    path('logout/', views.log_out, name="log_out"),

]

