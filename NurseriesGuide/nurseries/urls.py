from django.urls import path
from . import views


app_name = "nurseries"

urlpatterns = [
    path("",views.nurseries_view,name="nurseries_view"),
    path("add/",views.add_nurseries,name="add_nursery"),
    path("update/<int:nursery_id>/",views.update_nursery,name="update_nurseries"),
    path("delete/<int:nursery_id>/",views.delete_nursery,name="delete_nursery"),
    path("detail/<int:nursery_id>/",views.detail_nursery,name="nursery_detail"),
    path("add/<int:nursery_id>/activity",views.add_nurseries,name="add_activity"),
    path("update/<int:activity_id>/",views.update_activity,name="update_activity"),
    path("delete/<int:activity_id>/",views.delete_activity,name="delete_activity"),

]