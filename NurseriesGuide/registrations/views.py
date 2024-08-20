from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Registration
from .forms import RegistrationForm, RegistrationStatusForm,SubscriptionForm
from parents.models import Child
from .models import Nursery, Subscription




# @login_required
# def registration_create(request):
#     # Ensure the parent has at least one child before allowing registration
#     if not Child.objects.filter(parent__user=request.user).exists():
#         messages.warning(request, 'You must add at least one child before making a registration.', 'alert-warning')
#         return redirect('add_child')  # Assuming you have a view named 'add_child' for adding children

#     if request.method == 'POST':
#         form = RegistrationForm(request.POST)
#         if form.is_valid():
#             registration = form.save(commit=False)
#             registration.save()
#             messages.success(request, 'تم التسجيل بنجاح', 'alert-success')
#             return redirect('registration_detail', pk=registration.pk)
#         else:
#             messages.error(request, 'حدث خطأ ما', 'alert-danger')
#     else:
#         form = RegistrationForm()

#     return render(request, 'registrations/registration_form.html', {'form': form})



@login_required
def registration_create(request):
    if request.method == 'POST':
        child_id = request.POST.get('child')
        subscription_id = request.POST.get('subscription_id')  # Make sure this is passed from the form

        child = Child.objects.get(id=child_id)
        subscription = Subscription.objects.get(id=subscription_id)

        Registration.objects.create(
            child=child,
            subscription=subscription,
            status='reviewing'
        )
        return redirect('main:home') 
    return render(request, 'nurseries/nursery_detail.html') 


@login_required
def registration_list(request):
    registrations = Registration.objects.filter(child__parent__user=request.user)
    return render(request, 'registrations/registration_list.html', {'registrations': registrations})





@login_required
def registration_detail(request, pk):
    registration = get_object_or_404(Registration, pk=pk)
    return render(request, 'registrations/registration_detail.html', {'registration': registration})





@login_required
def registration_update_status(request, pk):
    registration = get_object_or_404(Registration, pk=pk)
    
    # Ensure the user is a manager of the nursery related to the registration
    if request.user != registration.subscription.nursery.owner:
        messages.error(request, 'لا تملك الصلاحية', 'alert-warning')
        return redirect('registration_detail', pk=registration.pk)

    if request.method == 'POST':
        form = RegistrationStatusForm(request.POST, instance=registration)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الحالة بنجاح', 'alert-success')
            return redirect('registration_detail', pk=registration.pk)
        else:
            messages.error(request, 'حدث خطأ ما', 'alert-danger')
    else:
        form = RegistrationStatusForm(instance=registration)

    return render(request, 'registrations/nursery_detail.html', {'form': form, 'registration': registration})


def add_subscription(request, nursery_id):
    nursery = get_object_or_404(Nursery, pk=nursery_id)
    
    if request.user != nursery.owner:
        return redirect("main:home")
    if request.method == 'POST':
        subscriptionForm = SubscriptionForm(request.POST)
        if subscriptionForm.is_valid():
            subscription = subscriptionForm.save(commit=False)  # Get the unsaved Activity instance
            subscription.nursery=nursery  # Set the nursery for this activity            
            subscription.save()  # Now save the Activity instance into the database
            messages.success(request, 'Activity added successfully!', 'alert-success')
            return redirect('nurseries:nursery_detail', nursery_id=nursery_id)
        else:
            for field, errors in subscriptionForm.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}", 'alert-danger')
    else:
        subscriptionForm = subscriptionForm()

    return render(request, 'nurseries/nursery_detail.html', {'subscriptionForm': subscriptionForm, 'nursery': nursery})
