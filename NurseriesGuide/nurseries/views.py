from django.shortcuts import render,redirect
from django.http import HttpRequest,HttpResponse
from .forms import NurseryForm,ActivityForm,StaffForm,GalleryForm,NurseryOwnerForm
from django.contrib import messages 
from nurseries.models import Activity,City,Neighborhood,Nursery,Gallery,Staff
from django.core.paginator import Paginator
from django.db.models import Avg,Sum,Max,Min,Count, Q

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
            messages.success(request, f'تم أضافة الحضانة{nursery.name}  بنجاح  !','alert-success')
            return redirect("nurseries:nurseries_view")
         else:    
            for field, errors in nurseryForm.errors.items():
                 for error in errors:
                     messages.error(request, f"{field}: {error}",'alert-danger')
        return render(request, "nurseries/nurseries_view.html",{"nurseryForm":nurseryForm,"neighborhoods":neighborhoods})  
    
def delete_nursery(request:HttpRequest,nursery_id:int):
    nursery = Nursery.objects.get(pk=nursery_id)
    if nursery.delete():
             messages.success(request, f'تم حذف حضانة {nursery.name}  بنجاح !',"alert-success")
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
             messages.success(request, 'تم حفظ تعديلاتك بنجاح  !',"alert-success")
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
            messages.success(request, f'تم أضافة النشاط{activity.name} بنجاج  !', 'alert-success')
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
    messages.success(request, f'تم حذف النشاط {activity.name} بنجاج  !', 'alert-success')
    return redirect('nurseries:nursery_detail', nursery_id=nursery_id)


def update_activity(request:HttpRequest, activity_id:int):
    activity = Activity.objects.get(pk=activity_id)
    if request.method == 'POST':
        activityForm = ActivityForm(request.POST, request.FILES, instance=activity)
        if activityForm.is_valid():
            activityForm.save()
            messages.success(request, '  تم حفظ تعديلاتك بنجاح!', 'alert-success')
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
            messages.success(request, f' تم أضافة العضو {staff.first_name} بنجاح   !', 'alert-success')
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
    messages.success(request, f' تم حذف العضو {staff.first_name} بنجاح   !', 'alert-success')
    return redirect('nurseries:nursery_detail', nursery_id=nursery_id)

def update_staff(request: HttpRequest, staff_id: int):

    staff = Staff.objects.get(pk=staff_id)
    if request.method == 'POST':
        staffForm = StaffForm(request.POST, request.FILES, instance=staff)
        if staffForm.is_valid():
            staffForm.save()
            messages.success(request, 'تم حفظ تعديلاتك بنجاح!', 'alert-success')
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
            messages.success(request, 'تمت الاضافة بنجاح !', 'alert-success')
            return redirect('nurseries:nursery_detail', nursery_id=nursery_id)


        else:
            for field, errors in galleryForm.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}", 'alert-danger')
    else:
        galleryForm = GalleryForm()

    return render(request, 'nurseries/nursery_detail.html', {'galleryForm': galleryForm, 'nursery': nursery})



def chlidren_requests(request):
    if not request.user.is_authenticated or not request.user.is_staff:
     return redirect("main:home")
    return render(request, "nurseries/chlidren_requests.html")











from django.views.generic import ListView
from .models import Nursery
from registrations.models import Review



# def nurseries_list(request):
#     nurseries = Nursery.objects.all()

#     # Check if there are any nurseries in the database
#     has_nurseries = nurseries.exists()

#     # Fetch distinct filter values from the database
#     ages = Nursery.objects.values_list('age_group', flat=True).distinct()
#     cities = Nursery.objects.values_list('city', flat=True).distinct()
#     neighborhoods = Nursery.objects.values_list('neighborhood', flat=True).distinct()

#     # Handle filtering
#     age = request.GET.get('age', '')
#     city = request.GET.get('city', '')
#     neighborhood = request.GET.get('neighborhood', '')
#     special_needs = request.GET.get('special_needs', '')

#     if age:
#         nurseries = nurseries.filter(age_group=age)
#     if city:
#         nurseries = nurseries.filter(city=city)
#     if neighborhood:
#         nurseries = nurseries.filter(neighborhood=neighborhood)
#     if special_needs:
#         nurseries = nurseries.filter(special_needs=True)

#     # Handle search
#     search_term = request.GET.get('searched', '')
#     if search_term:
#         nurseries = nurseries.filter(Q(name__icontains=search_term) | Q(description__icontains=search_term))

#     # Handle pagination
#     paginator = Paginator(nurseries, 6)  # 6 nurseries per page
#     page_number = request.GET.get('page')
#     paginated_nurseries = paginator.get_page(page_number)

#     # Calculate average rating for each nursery
#     for nursery in paginated_nurseries:
#         avg_rating = nursery.reviews.aggregate(Avg('rating'))['rating__avg']
#         nursery.avg_rating = avg_rating if avg_rating else 0

#     context = {
#         'nurseries': paginated_nurseries,
#         'search_term': search_term,
#         'age': age,
#         'city': city,
#         'neighborhood': neighborhood,
#         'special_needs': special_needs,
#         'ages': ages,
#         'cities': cities,
#         'neighborhoods': neighborhoods,
#         'has_nurseries': has_nurseries,
#     }

#     return render(request, 'nurseries/nurseries_list.html', context)



def nurseries_list(request):
    nurseries = Nursery.objects.all()

    # Check if there are any nurseries in the database
    has_nurseries = nurseries.exists()

    # Fetch distinct filter values from the related models
    # Assuming you want to filter by city and neighborhood from related Neighborhood model
    cities = Neighborhood.objects.values_list('city__name', flat=True).distinct()
    neighborhoods = Neighborhood.objects.values_list('name', flat=True).distinct()

    # Handle filtering
    city = request.GET.get('city', '')
    neighborhood = request.GET.get('neighborhood', '')
    special_needs = request.GET.get('special_needs', '')

    if city:
        nurseries = nurseries.filter(neighborhood__city__name=city)
    if neighborhood:
        nurseries = nurseries.filter(neighborhood__name=neighborhood)
    if special_needs:
        nurseries = nurseries.filter(accepts_special_needs=True)

    # Handle search
    search_term = request.GET.get('searched', '')
    if search_term:
        nurseries = nurseries.filter(Q(name__icontains=search_term) | Q(description__icontains=search_term))

    # Handle pagination
    paginator = Paginator(nurseries, 3) 
    page_number = request.GET.get('page')
    paginated_nurseries = paginator.get_page(page_number)

    # Calculate average rating for each nursery
    for nursery in paginated_nurseries:
        avg_rating = nursery.reviews.aggregate(Avg('rating'))['rating__avg']
        nursery.avg_rating = avg_rating if avg_rating else 0

    context = {
        'nurseries': paginated_nurseries,
        'search_term': search_term,
        'city': city,
        'neighborhood': neighborhood,
        'special_needs': special_needs,
        'cities': cities,
        'neighborhoods': neighborhoods,
        'has_nurseries': has_nurseries,
    }

    return render(request, 'nurseries/nurseries_list.html', context)
    



    
class NurseriesListView(ListView):
    model = Nursery
    template_name = 'nurseries/nurseries_list.html'
    context_object_name = 'nurseries'
    paginate_by = 6  # Number of nurseries per page

    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = self.request.GET.get('searched', '')
        if search_term:
            queryset = queryset.filter(name__icontains=search_term)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        nurseries = context['nurseries']
        
        # Calculate average rating for each nursery
        for nursery in nurseries:
            avg_rating = nursery.reviews.aggregate(Avg('rating'))['rating__avg']
            nursery.avg_rating = avg_rating if avg_rating else 0
        
        context['search_term'] = self.request.GET.get('searched', '')
        return context











