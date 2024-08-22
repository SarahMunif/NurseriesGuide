from django.urls import path
from . import views


app_name = "nurseries"


urlpatterns = [
    path("view",views.nurseries_view,name="nurseries_view"),
    path("",views.nurseries_list,name="nurseries_list"),
    path("requests-admin/",views.verify_nurseries,name="verify_nurseries"),
    path("owner/requests/",views.owner_requests_view,name="owner_requests_view"),

    path("chlidren/requests/", views.children_requests, name="children_requests"),
    
    path("add/",views.add_nursery,name="add_nursery"),
    path("update/<int:nursery_id>/",views.update_nursery,name="update_nursery"),
    path("delete/<int:nursery_id>/",views.delete_nursery,name="delete_nursery"),
    path("detail/<int:nursery_id>/",views.detail_nursery,name="nursery_detail"),
    
    path("add/<int:nursery_id>/activity",views.add_activity,name="add_activity"),
    path("update/<int:activity_id>/activity/",views.update_activity,name="update_activity"),
    path("delete/<int:activity_id>/activity/",views.delete_activity,name="delete_activity"),

    path("add/<int:nursery_id>/staff/",views.add_staff,name="add_staff"),
    path("update/<int:staff_id>/staff/",views.update_staff,name="update_staff"),
    path("delete/<int:staff_id>/staff/",views.delete_staff,name="delete_staff"),

    path("add/<int:nursery_id>/gallery/", views.add_gallery, name="add_gallery"),
    
    path("check_out/<int:child_id>/",views.check_out, name="check_out"),
]