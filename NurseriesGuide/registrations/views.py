from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Registration
from .forms import RegistrationForm, RegistrationStatusForm
from parents.models import Child




@login_required
def registration_create(request):
    # Ensure the parent has at least one child before allowing registration
    if not Child.objects.filter(parent__user=request.user).exists():
        messages.warning(request, 'You must add at least one child before making a registration.', 'alert-warning')
        return redirect('add_child')  # Assuming you have a view named 'add_child' for adding children

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.save()
            messages.success(request, 'تم التسجيل بنجاح', 'alert-success')
            return redirect('registration_detail', pk=registration.pk)
        else:
            messages.error(request, 'حدث خطأ ما', 'alert-danger')
    else:
        form = RegistrationForm()

    return render(request, 'registrations/registration_form.html', {'form': form})





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
    if request.user != registration.subscription.nursery.manager:
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

    return render(request, 'registrations/registration_status_form.html', {'form': form, 'registration': registration})

