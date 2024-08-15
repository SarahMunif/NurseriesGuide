from django.urls import path
from . import views

app_name = "parents"

urlpatterns = [

    path('add/', views.add_child, name="add_child"),
    path('update/', views.update_parent, name="update_parent"),
    path('delete/child/', views.delete_child, name="delete_child"),
    path('update/child/', views.update_child, name="update_child"),

]

