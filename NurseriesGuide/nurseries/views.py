from django.shortcuts import render,redirect
from django.http import HttpRequest,HttpResponse
from .forms import NurseryForm,ActivityForm,StaffForm,GalleryForm,NurseryOwnerForm
from django.contrib import messages 
from nurseries.models import Activity,City,Neighborhood,Nursery,Gallery,Staff
from django.core.paginator import Paginator
from django.contrib import messages 
from django.db.models import Avg,Sum,Max,Min
from django.db.models import Q

from registrations.models import Subscription
# Create your views here.

# nursery model views 

def nurseries_view(request:HttpRequest):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect("main:home")  # Redirect non-staff users to home page

    nurseries = Nursery.objects.filter(owner=request.user)
    nurseries = Nursery.objects.filter(status='verified')
    
    neighborhoods = Neighborhood.objects.all()

    
    # Check if a search was made
    searched = request.GET.get('searched', '')
    if searched:
        nurseries = nurseries.filter(name__icontains=searched)


    page_number = request.GET.get("page", 1)
    paginator = Paginator(nurseries, 6)
    nurseries = paginator.get_page(page_number)   
    if request.user.is_staff:
     return render(request, "nurseries/nurseries_view.html", {"nurseries" : nurseries,"search_term": searched,"neighborhoods":neighborhoods})
    if not request.user.is_staff:
      return render(request, "main/home.html", {"nurseries" : nurseries ,"search_term": searched })

def verify_nurseries(request):
    if not request.user.is_superuser:
        return redirect('main:home') 
    else:
        if request.method == 'POST':
            nursery_id = request.POST.get('nursery_id')
            action = request.POST.get('action', 'verify')
            rejection_reason = request.POST.get('rejection_reason', '')

            if nursery_id:
                nursery = Nursery.objects.get(id=nursery_id)
                if action == 'verify':
                    nursery.verified = True
                    nursery.status = 'verified'
                elif action == 'reject':
                    nursery.verified = False
                    nursery.status = 'rejected'
                    nursery.rejection_reason = rejection_reason

                nursery.save()
                return redirect('nurseries:verify_nurseries')
            else:
                messages.error(request, "No nursery selected.")

        unverified_nurseries = Nursery.objects.filter(status='pending')
        return render(request, "nurseries/superuser_nurseries.html", {
            "unverified_nurseries": unverified_nurseries
        })

def owner_requests_view(request):
    if not request.user.is_authenticated or not request.user.is_staff:
     return redirect("main:home")  # Redirect non-staff users to home page

    nurseries = Nursery.objects.filter(owner=request.user)
    neighborhoods = Neighborhood.objects.all()

    unverified_nurseries = nurseries.filter(Q(status='pending') | Q(status='rejected'))    
    return render(request, "nurseries/owner_requests.html", {
            "unverified_nurseries": unverified_nurseries,"neighborhoods":neighborhoods
        })



def add_nursery(request:HttpRequest):
        if not request.user.is_authenticated or not request.user.is_staff:
           return redirect("main:home")  # Redirect non-staff users to home page
        neighborhoods = Neighborhood.objects.all()

        if request.method=="POST":
         nurseryForm=NurseryOwnerForm(request.POST,request.FILES)
         if nurseryForm.is_valid():
            nursery = nurseryForm.save(commit=False)
            nursery.owner = request.user  # Set the owner to the current user  
            nursery.save()           
            messages.success(request, 'nursery added successfully!','alert-success')
            return redirect("nurseries:nurseries_view")
         else:    
            for field, errors in nurseryForm.errors.items():
                 for error in errors:
                     messages.error(request, f"{field}: {error}",'alert-danger')
        return render(request, "nurseries/nurseries_view.html",{"nurseryForm":nurseryForm,"neighborhoods":neighborhoods})  
    
def delete_nursery(request:HttpRequest,nursery_id:int):
    nursery = Nursery.objects.get(pk=nursery_id)
    if nursery.delete():
             messages.success(request, 'nursery deleted successfully!',"alert-success")
             return redirect('nurseries:nurseries_view')
    else:
         for field, errors in nursery.errors.items():
             for error in errors:
                 messages.error(request, f"{field}: {error}","alert-danger")    
    return redirect('nurseries:nurseries_view')

def update_nursery(request:HttpRequest,nursery_id:int):
    nursery = Nursery.objects.get(pk=nursery_id)
    if request.method == "POST":
         nurseryForm=NurseryOwnerForm(request.POST, request.FILES, instance=nursery)
         if nurseryForm.is_valid():
             nurseryForm.save()
             messages.success(request, 'nursery updated successfully!',"alert-success")
             return redirect("nurseries:nurseries_view")
         else:
             for field, errors in nurseryForm.errors.items():
                 for error in errors:
                     messages.error(request, f"{field}: {error}","alert-danger")
    return render(request, "nurseries/nurseries_view.html")
      

def detail_nursery(request:HttpRequest,nursery_id:int):
    nursery = Nursery.objects.get(pk=nursery_id)
    staffs=nursery.staff_set.all() 
    gallery_items=nursery.gallery_set.all() 
    subscriptions = nursery.subscriptions.all()

    # this calculate the min and max age the nursery takes based on the activities it offers
    activities = nursery.activity_set.all() 
    min = activities.aggregate(Min('age_min'))  # This will return a dictionary
    max = activities.aggregate(Max('age_max'))  
    
    min = min['age_min__min']  # Extract the  age from the dictonary for a better disply in the web bage
    max = max['age_max__max']  
    
    # Pass the nursery and the calculated ages to the template
    return render(request, "nurseries/nursery_detail.html", {
        "nursery": nursery,
        "min": min,
        "max": max,
        "activities":activities,
        "staffs":staffs,
        "gallery_items":gallery_items,
        "subscriptions":subscriptions
    })
# activity model views 

def add_activity(request:HttpRequest,nursery_id:int):
    nursery = Nursery.objects.get(pk=nursery_id)

    if request.method == 'POST':
        activityForm = ActivityForm(request.POST, request.FILES)
        if activityForm.is_valid():
            activity = activityForm.save(commit=False)  # Get the unsaved Activity instance
            activity.nursery=nursery  # Set the nursery for this activity            
            activity.save()  # Now save the Activity instance into the database
            messages.success(request, 'Activity added successfully!', 'alert-success')
            return redirect('nurseries:nursery_detail', nursery_id=nursery_id)
        else:
            for field, errors in activityForm.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}", 'alert-danger')
    else:
        activityForm = ActivityForm()

    return render(request, 'nurseries/nursery_detail.html', {'activityForm': activityForm, 'nursery': nursery})

def delete_activity(request:HttpRequest, activity_id:int):
    activity = Activity.objects.get(pk=activity_id)
    nursery_id = activity.nursery.id  
    activity.delete()
    messages.success(request, 'Activity deleted successfully!', 'alert-success')
    return redirect('nurseries:nursery_detail', nursery_id=nursery_id)


def update_activity(request:HttpRequest, activity_id:int):
    activity = Activity.objects.get(pk=activity_id)
    if request.method == 'POST':
        activityForm = ActivityForm(request.POST, request.FILES, instance=activity)
        if activityForm.is_valid():
            activityForm.save()
            messages.success(request, 'Activity updated successfully!', 'alert-success')
            return redirect('nurseries:nursery_detail', nursery_id=activity.nursery_id)
        else:
            for field, errors in activityForm.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}", 'alert-danger')
    else:
        activityForm = ActivityForm(instance=activity)
    
    return render(request, 'nurseries/detail_nursery.html', {'activityForm': activityForm, 'activity': activity})

# staff model views 

def add_staff(request: HttpRequest, nursery_id: int):
    nursery = Nursery.objects.get(pk=nursery_id)
    if request.method == 'POST':
        staffForm = StaffForm(request.POST, request.FILES)
        if staffForm.is_valid():
            staff = staffForm.save(commit=False)
            staff.nursery = nursery
            staff.save()
            messages.success(request, 'Staff member added successfully!', 'alert-success')
            return redirect('nurseries:nursery_detail', nursery_id=nursery_id)
        else:
            for field, errors in staffForm.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}", 'alert-danger')
    else:
        staffForm = StaffForm()

    return render(request, 'nurseries/nursery_detail.html', {'staffForm': staffForm, 'nursery': nursery})

def delete_staff(request: HttpRequest, staff_id: int):
    staff = Staff.objects.get(pk=staff_id)
    nursery_id = staff.nursery.id  # Store the nursery id to redirect after deletion
    staff.delete()
    messages.success(request, 'Staff member deleted successfully!', 'alert-success')
    return redirect('nurseries:nursery_detail', nursery_id=nursery_id)

def update_staff(request: HttpRequest, staff_id: int):

    staff = Staff.objects.get(pk=staff_id)
    if request.method == 'POST':
        staffForm = StaffForm(request.POST, request.FILES, instance=staff)
        if staffForm.is_valid():
            staffForm.save()
            messages.success(request, 'Staff member updated successfully!', 'alert-success')
            return redirect('nurseries:nursery_detail', nursery_id=staff.nursery_id)
        else:
            for field, errors in staffForm.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}", 'alert-danger')
    else:
        staffForm = StaffForm(instance=staff)

    return render(request, 'nurseries/nursery_detail.html', {'staffForm': staffForm, 'staff': staff})



def add_gallery(request: HttpRequest, nursery_id: int):
    nursery = Nursery.objects.get(pk=nursery_id)
    if request.method == 'POST':
        galleryForm = GalleryForm(request.POST, request.FILES)
        if galleryForm.is_valid():
            gallery = galleryForm.save(commit=False)
            gallery.nursery = nursery  # Assuming the Gallery model has a ForeignKey to Nursery
            gallery.save()
            messages.success(request, 'Gallery image added successfully!', 'alert-success')
            return redirect('nurseries:nursery_detail', nursery_id=nursery_id)


        else:
            for field, errors in galleryForm.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}", 'alert-danger')
    else:
        galleryForm = GalleryForm()

    return render(request, 'nurseries/nursery_detail.html', {'galleryForm': galleryForm, 'nursery': nursery})








def nurseries_list(request):
    
    nurseries = Nursery.objects.all()
    neighborhoods = Neighborhood.objects.all()

    # Check if a search was made
    searched = request.GET.get('searched', '')
    if searched:
        nurseries = nurseries.filter(name__icontains=searched)

    # Pagination
    page_number = request.GET.get("page", 1)
    paginator = Paginator(nurseries, 6)
    nurseries_page = paginator.get_page(page_number)

    # Add average rating for each nursery
    for nursery in nurseries_page:
        avg_rating = nursery.review_set.aggregate(Avg('rating'))['rating__avg']
        nursery.avg_rating = avg_rating if avg_rating is not None else 0

    return render(request, "nurseries/nurseries_list.html", {
        "nurseries": nurseries_page,
        "search_term": searched,
        "neighborhoods": neighborhoods
    })





