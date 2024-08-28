from django.shortcuts import render,redirect
from django.http import HttpRequest,HttpResponse
from .forms import NurseryForm,ActivityForm,StaffForm,GalleryForm,NurseryOwnerForm
from django.contrib import messages 
from nurseries.models import Activity,Neighborhood,Nursery,Staff,Gallery
from django.core.paginator import Paginator
from django.db.models import Avg,Max,Min, Q,Count,Sum,ExpressionWrapper, DecimalField
from django.urls import reverse
from registrations.models import Registration
from parents.models import Child
import stripe

from django.contrib.auth.models import User
from django.db.models.functions import TruncMonth
from decimal import Decimal

# Create your views here.

# nursery model views 

def nurseries_view(request:HttpRequest):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect("main:home")  # Redirect non-staff users to home page

    user_nurseries = Nursery.objects.filter(owner=request.user)
    nurseries = user_nurseries.filter(status='verified')
    
    neighborhoods = Neighborhood.objects.all()

    registrations_reviewing = Registration.objects.filter(
        subscription__nursery__in=user_nurseries,
        status='reviewing'
    )
    registrations_count = registrations_reviewing.count()

    # Check if a search was made
    searched = request.GET.get('searched', '')
    if searched:
        nurseries = nurseries.filter(name__icontains=searched)


    page_number = request.GET.get("page", 1)
    paginator = Paginator(nurseries, 6)
    nurseries = paginator.get_page(page_number)   
    if request.user.is_staff:
     return render(request, "nurseries/nurseries_view.html", {"nurseries" : nurseries,"search_term": searched,"neighborhoods":neighborhoods , "registrations_count":registrations_count})
    if not request.user.is_staff:
      return render(request, "main/home.html", {"nurseries" : nurseries ,"search_term": searched  })

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

    registrations_reviewing = Registration.objects.filter(
        subscription__nursery__in=nurseries,
        status='reviewing'
    )
    
    registrations_count = registrations_reviewing.count()
    unverified_nurseries = nurseries.filter(Q(status='pending') | Q(status='rejected'))    
    return render(request, "nurseries/owner_requests.html", {
            "unverified_nurseries": unverified_nurseries,"neighborhoods":neighborhoods,
            "registrations_count":registrations_count
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
            min_age = int(request.POST['min_age'])
            max_age = int(request.POST['max_age'])
            if 'min_age_years' in request.POST:
                min_age *= 12    # to be as months to better the search filltring later 
            if 'max_age_years' in request.POST:
                max_age *= 12 
            nursery.min_age=min_age    # age in months 
            nursery.max_age=max_age                           
            nursery.save()           
            messages.success(request, f'تم أضافة الحضانة{nursery.name}  بنجاح  ! يمكنك تتبع حاله الطلب في "طلباتي"','alert-success')
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
            if 'main_image' in request.FILES:
                nurseryForm.main_image = request.FILES['main_image']
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
    reviews= nursery.reviews.all()
    
    is_owner = request.user == nursery.owner # to restrict the update icons in the frontend for the owner only

    activities = nursery.activity_set.all() 

    average_rating = nursery.reviews.aggregate(Avg('rating'))
    average_rating = average_rating['rating__avg']  
    if average_rating:
     average_rating= round(average_rating) 


    min=nursery.min_age 
    if min >= 12:
        min=int(min/12) 
        min_unit="سنوات" 
    else:
      min_unit="أشهر" 
    max=nursery.max_age
    if max >= 12:
        max=int(max/12)
        max_unit="سنوات"  
    else:
      max_unit="أشهر"
    
    for subscription in subscriptions:
        age_min = subscription.age_min
        if age_min >= 12:
            age_min = int(age_min / 12)
            min_unit = "سنوات"
        else:
            min_unit = "أشهر"
        subscription.min_display = f"{age_min} {min_unit}"

        age_max = subscription.age_max
        if age_max >= 12:
            age_max = int(age_max / 12)
            max_unit = "سنوات"
        else:
            max_unit = "أشهر"
        nursery.max_display = f"{age_max} {max_unit}"

    return render(request, "nurseries/nursery_detail.html", {
        "nursery": nursery,

        "activities":activities,
        "staffs":staffs,
        "gallery_items":gallery_items,
        "subscriptions":subscriptions,
        "reviews":reviews,
        "is_owner":is_owner,
        "average_rating": average_rating if average_rating is not None else "  لا توجد تقييمات ",
        'min':min,
        "max":max,
        "max_unit":max_unit,
        "min_unit":min_unit,
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
            return redirect('nurseries:nursery_detail', nursery_id=nursery_id)
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




def children_requests(request):
    if not request.user.is_staff:
        return redirect("main:home")
    
    # Fetch all nurseries owned by the logged-in user
    user_nurseries = Nursery.objects.filter(owner=request.user)
    # Fetch registrations linked to any of the nurseries owned by the user
    registrations = Registration.objects.filter(subscription__nursery__in=user_nurseries).order_by('-created_at')


    registrations_reviewing = Registration.objects.filter(
        subscription__nursery__in=user_nurseries,
        status='reviewing'
    )
    
    registrations_count = registrations_reviewing.count()
    
    return render(request, "nurseries/children_requests.html", {    
        'registrations': registrations,
        'status_choices': Registration.STATUS_CHOICES ,
         "registrations_count":registrations_count })











def nurseries_list(request):
    nurseries = Nursery.objects.filter(status='verified').annotate(avg_rating=Avg('reviews__rating'))

    # Handle filtering by city, neighborhood, and special needs
    city = request.GET.get('city', '')
    neighborhood = request.GET.get('neighborhood', '')
    special_needs = request.GET.get('special_needs', '')
    min_rating = request.GET.get('min_rating', None)  # Retrieve the minimum rating from the request
    age_range= request.GET.get('age_range', None)
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

    # Filter by minimum rating if specified
    if min_rating:
        nurseries = nurseries.annotate(avg_rating=Avg('reviews__rating')).filter(avg_rating__gte=min_rating)

    # Check if there are any nurseries after filtering
    has_nurseries = nurseries.exists()

    # Fetch distinct cities and neighborhoods for filtering options
    cities = Neighborhood.objects.values_list('city__name', flat=True).distinct()
    neighborhoods = Neighborhood.objects.values_list('name', flat=True).distinct()
    if city: neighborhoods = Neighborhood.objects.filter(city__name=city).values_list('name', flat=True).distinct()
    if age_range:
        age_min, age_max = map(int, age_range.split('-'))  # split the values in the html the first value is the min , the last is the max
        nurseries = nurseries.filter(min_age__lte=age_max, max_age__gte=age_min) # get the nurseries the have range between the min and max 
    # Handle pagination
    for nursery in nurseries:
        nursery.gallery_items = Gallery.objects.filter(nursery=nursery)[:1]
 
        min_age = nursery.min_age
        if min_age >= 12:
            min_age = int(min_age / 12)
            min_unit = "سنوات"
        else:
            min_unit = "أشهر"
        nursery.min_display = f"{min_age} {min_unit}"

        max_age = nursery.max_age
        if max_age >= 12:
            max_age = int(max_age / 12)
            max_unit = "سنوات"
        else:
            max_unit = "أشهر"
        nursery.max_display = f"{max_age} {max_unit}"
    paginator = Paginator(nurseries, 3)
    page_number = request.GET.get('page')
    paginated_nurseries = paginator.get_page(page_number)


    context = {
        'nurseries': paginated_nurseries,
        'search_term': search_term,
        'city': city,
        'neighborhood': neighborhood,
        'special_needs': special_needs,
        'cities': cities,
        'neighborhoods': neighborhoods,
        'has_nurseries': has_nurseries,
        "min_rating":min_rating,
        "age_range":age_range
    }

    return render(request, 'nurseries/nurseries_list.html', context)

    
stripe.api_key = 'sk_test_51PqVngP8jLmG3xUuIatGR7XDz6rs78kHUkJEsjuRcP6uWTgHfTO90A7K2eryyYVrgKng8DyThSmLzyzDigfSKcN100PEjWeSLg'



def check_out(request, child_id):
        # Fetch the child and their subscription
        child = Child.objects.get(id=child_id)
        registration = Registration.objects.filter(child=child).first()
        if not registration:
            # Redirect or handle the error as needed
            return redirect('main:home')

        subscription = registration.subscription

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'sar',
                    'product_data': {
                        'name': ' {}'.format(child.first_name),
                    },
                    'unit_amount': int(subscription.price * 100),  # Stripe requires the amount in cents
                },
                'quantity': 1,
            }],
            mode='payment',
        success_url=request.build_absolute_uri(reverse('nurseries:payment_success', args=[child_id])),
        cancel_url=request.build_absolute_uri(reverse('nurseries:payment_cancel', args=[child_id])),
    )


        # Redirect to the Stripe checkout
        return redirect(checkout_session.url)


def payment_success(request, child_id):
    child = Child.objects.get(id=child_id)
    registration = Registration.objects.filter(child=child).first()
    registration.status="accepted"
    registration.save() 
    return redirect("parents:requests_status")

def payment_cancel(request, child_id):
        return redirect("parents:requests_status")






def owner_nursery_statistics(request):
    if not request.user.is_staff:
        return redirect('main:home')
    
    verify_nurseries = Nursery.objects.filter(status='verified')
    nurseries = verify_nurseries.filter(owner=request.user).annotate(
        total_children=Count('subscriptions__registrations__child', distinct=True),
        total_registrations=Count('subscriptions__registrations'),
        accepted_registrations=Count('subscriptions__registrations', filter=Q(subscriptions__registrations__status='accepted')),
        rejected_registrations=Count('subscriptions__registrations', filter=Q(subscriptions__registrations__status='rejected')),
    )
    registrations_reviewing = Registration.objects.filter(
        subscription__nursery__in=verify_nurseries,
        status='reviewing'
    )
    registrations_count = registrations_reviewing.count()

    chart_data = {
        'labels': [nursery.name for nursery in nurseries],
        'children_count': [nursery.total_children for nursery in nurseries],
        'registrations': {
            'total': [nursery.total_registrations for nursery in nurseries],
            'accepted': [nursery.accepted_registrations for nursery in nurseries],
            'rejected': [nursery.rejected_registrations for nursery in nurseries],
        }
    }
    
    nursery_status_counts = Nursery.objects.filter(owner=request.user).values('status').annotate(total=Count('id')).order_by()
    nurseries_status_labels = dict(Nursery._meta.get_field('status').choices)  # Corrected access to choices
    
    pie_chart_data = {
        'labels': [nurseries_status_labels.get(status['status'], 'Unknown') for status in nursery_status_counts],
        'values': [status['total'] for status in nursery_status_counts],
    }
    
    registrations = Registration.objects.filter(subscription__nursery__owner=request.user)
    status_counts = registrations.values('status').annotate(total=Count('id')).order_by()
    
    registrations_status_labels = dict(Registration.STATUS_CHOICES)
    
    registrations_pie_chart_data = {
        'labels': [registrations_status_labels.get(status['status']) for status in status_counts],
        'values': [status['total'] for status in status_counts],
    }
    
    return render(request, 'nurseries/statistics.html', {
        'chart_data': chart_data,
        'pie_chart_data': pie_chart_data,
        'registrations_pie_chart_data': registrations_pie_chart_data,
        "registrations_count":registrations_count
    })




def admin_nursery_statistics(request):
    parent_count = User.objects.count() # all users count
    
    # Query verified nurseries
    # verify_nurseries = Nursery.objects.filter(status='verified') 
    # nurseries_count = verify_nurseries.count() 

    # Calculate total profits
    registration = Registration.objects.filter(status="accepted")
    total_price = registration.aggregate(total_price=Sum('subscription__price'))['total_price']
    total_profit = Decimal('0.00') if total_price is None else total_price * Decimal('0.1')

    # Query accepted registrations and aggregate monthly revenue
    registrations = Registration.objects.filter(status="accepted")
    monthly_revenue = registrations.annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        total_price=ExpressionWrapper(
            Sum('subscription__price') * Decimal('0.1'),
            output_field=DecimalField()
        )
    ).order_by('month')

    # Convert to list to pass to template
    months = [revenue['month'].strftime("%Y-%m") for revenue in monthly_revenue]
    prices = [float(revenue['total_price']) for revenue in monthly_revenue]

    # Calculate the difference in profits between the last two months

    if len(prices) >= 2:
        profit_difference = prices[-1] - prices[-2]
    else:
        profit_difference = 0  # Default to 0 if not enough data

    unverified_nurseries = Nursery.objects.filter(status='pending')
    unverified_count=unverified_nurseries.count()

    # Calculate the number of new users per month using 'date_joined'
    user_stats = User.objects.annotate(
        month=TruncMonth('date_joined')
    ).values('month').annotate(
        user_count=Count('id')
    ).order_by('month')

    user_months = [user['month'].strftime("%Y-%m") for user in user_stats]
    user_counts = [user['user_count'] for user in user_stats]
    # Calculate the difference in user registrations between the last two months
    if len(user_counts) >= 2:
        user_count_difference = user_counts[-1] - user_counts[-2]
    else:
        user_count_difference = 0  # Default to 0 if not enough data

    return render(request, 'nurseries/admin_statistics.html', {
        "months": months,
        "prices": prices,
        "profit_difference": profit_difference,
        # "nurseries_count": nurseries_count,
        "total_profit": total_profit,
        "parent_count": parent_count,
        "user_months": user_months,
        "user_counts": user_counts,
        "user_count_difference": user_count_difference,
        "unverified_count":unverified_count

    })
##