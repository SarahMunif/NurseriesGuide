from django.shortcuts import render
from django.contrib import messages 
from django.shortcuts import render,redirect




def home(request):
    return render(request, 'main/home.html')



def staff_dashboard(request):
    if not request.user.is_staff:
        messages.success(request, "only staff can view this page", "alert-warning")
        return redirect("main:home_view")
    
    return render(request, 'main/staff_dashboard.html')

def admin_dashboard(request):
    if not request.user.is_admin:
        messages.success(request, "only staff can view this page", "alert-warning")
        return redirect("main:home_view")
    
    return render(request, 'main/admin_dashboard.html')