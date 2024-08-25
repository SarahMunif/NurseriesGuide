from django.shortcuts import render,redirect
from django.http import HttpRequest,HttpResponse
from .forms import NurseryForm,ActivityForm,StaffForm,GalleryForm,NurseryOwnerForm
from django.contrib import messages 
from nurseries.models import Activity,Neighborhood,Nursery,Staff
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

    # this calculate the min and max age the nursery takes based on the activities it offers
    activities = nursery.activity_set.all() 
    min = activities.aggregate(Min('age_min'))  # This will return a dictionary
    max = activities.aggregate(Max('age_max'))  
    

    average_rating = nursery.reviews.aggregate(Avg('rating'))
    average_rating = average_rating['rating__avg']  
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
        "subscriptions":subscriptions,
        "reviews":reviews,
        "is_owner":is_owner,
        "average_rating": average_rating if average_rating is not None else "  لا توجد تقييمات "
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
    
    
    return render(request, "nurseries/children_requests.html", {    
        'registrations': registrations,
        'status_choices': Registration.STATUS_CHOICES })









from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Avg, Q

def nurseries_list(request):
    nurseries = Nursery.objects.filter(status='verified')

    # Check if there are any nurseries in the database
    has_nurseries = nurseries.exists()

    # Fetch distinct filter values from the related models
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

    
stripe.api_key = ''



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
        'registrations_pie_chart_data': registrations_pie_chart_data
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

    })