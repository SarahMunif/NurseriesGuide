from django.shortcuts import render
from django.contrib import messages 
from django.shortcuts import render,redirect
from django.db.models import Count,Min,Max
from nurseries.models import Nursery,City,Activity,Gallery
from parents.models import Parent




def home(request):
     
    nurseries = Nursery.objects.filter(status='verified')[0:3]# only verfied nursires can be displayed
    nurseries_count = Nursery.objects.count()
    cities_count = City.objects.count()
    parents_count = Parent.objects.count()
    for nursery in nurseries:
        nursery.gallery_items = Gallery.objects.filter(nursery=nursery)[:1]
    # Get aggregate minimum and maximum ages from activities of verified nurseries
    activities = Activity.objects.filter(nursery__status='verified')
    min = activities.aggregate(Min('age_min'))['age_min__min']
    max = activities.aggregate(Max('age_max'))['age_max__max']

    return render(request, 'main/home.html',{"nurseries_count":nurseries_count,"cities_count":cities_count,"parents_count":parents_count,
                                             "nurseries":nurseries,"min":min,"max":max})


def about_us(request):
    return render(request, 'main/about_us.html')

def contact_us(request):
    return render(request, 'main/contact_us.html')



def staff_dashboard(request):
    if not request.user.is_staff:
        messages.success(request, "only staff can view this page", "alert-warning")
        return redirect("main:home")
    
    return render(request, 'main/staff_dashboard.html')

def admin_dashboard(request):
    if not request.user.is_superuser:
        messages.success(request, "only admin can view this page", "alert-warning")
        return redirect("main:home")
    
    return render(request, 'main/admin_dashboard.html')