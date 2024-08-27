from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Registration
from .forms import RegistrationForm, RegistrationStatusForm,SubscriptionForm,ReviewForm
from parents.models import Child
from .models import Nursery, Subscription,Review
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string


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
        subscription_id = request.POST.get('subscription_id')

        # Retrieve the child and subscription objects
        child = Child.objects.get(id=child_id)
        subscription = Subscription.objects.get(id=subscription_id)
        nurseryid = subscription.nursery.pk
        # if child.age not in range(subscription.age_min,subscription.age_max):
        #     age = child.age().split(' ')
        #     print("child",int(age[0]))
        #     print("allowed",subscription.age_min,subscription.age_max)
        #     messages.error(request, f'لايمكنك التسجيل في الحضانة لانها تقبل العمر بين {subscription.age_min} - {subscription.age_max}', "alert-warning")
        #     return redirect('nurseries:nursery_detail', nursery_id=nurseryid)


        # Check if a registration exists for this child with a status other than 'rejected'
        existing_registration = Registration.objects.filter(child=child).exclude(status='rejected').exists()

        if existing_registration:
            # If a registration exists that isn't rejected, do not create a new one
            messages.error(request, 'لا يمكنك إنشاء طلب جديد لأن هذا الطفل لديه بالفعل طلب تحت المراجعة أو مقبول.', "alert-warning")
            return redirect('nurseries:nursery_detail', nursery_id=nurseryid)
        else:
            try:

                # Create a new registration if the previous one is rejected or none exists
                registration = Registration.objects.create(
                    child=child,
                    subscription=subscription,
                    status='reviewing'
                )

                send_to = subscription.nursery.owner.email
                content_html = render_to_string("main/mail/send_request_to_owner.html",{"child":child,"subscription":subscription,"registration":registration})
                email_message = EmailMessage("لديك طلب جديد", content_html, settings.EMAIL_HOST_USER, [send_to])
                email_message.content_subtype = "html"
                email_message.send()
                messages.success(request, 'تم إنشاء طلب التسجيل بنجاح.', "alert-success")
                return redirect('parents:requests_status')
            except Exception as e :
                print(e)
                messages.error(request, 'حدث خطأ غير متوقع.', "alert-warning")
                return redirect('parents:requests_status')


    return render(request, 'nurseries/nursery_detail.html')


def delete_registration(request,registration_id:int):
    registration = Registration.objects.get(pk=registration_id)
    if registration.delete():
             messages.success(request, f'تم الغاء الطلب  بنجاح !',"alert-success")
             if request.user.is_staff:
                return redirect('nurseries:children_requests')
             else:
                return redirect('parents:requests_status')

    else:
         for field, errors in registration.errors.items():
             for error in errors:
                 messages.error(request, f"{field}: {error}","alert-danger")
    return redirect('nurseries:children_requests')


def registration_update_status(request, pk):
    registration = get_object_or_404(Registration, pk=pk)
    if request.method == 'POST':
        form = RegistrationStatusForm(request.POST, instance=registration)
        if form.is_valid():
            updated_registration = form.save(commit=False)
            updated_registration.save()
            messages.success(request, 'تم تحديث الحالة بنجاح.','alert-success')
            send_to = registration.child.parent.user.email
            content_html = render_to_string("main/mail/receive_request_from_owner.html",{"registration":registration})
            email_message = EmailMessage("تحديث حالة الطلب",content_html, settings.EMAIL_HOST_USER, [send_to])
            email_message.content_subtype = "html"
            email_message.send()
            messages.success(request, 'تم ارسال ايميل بحالة الطلب الجديدة لولي الامر  .',"alert-success")
            return redirect('nurseries:children_requests')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}",'alert-danger')
            else:
                form = RegistrationStatusForm(instance=registration)


    return render(request, 'nurseries/children_requests.html', {'form': form, 'registration': registration})

def add_subscription(request, nursery_id):
    nursery = get_object_or_404(Nursery, pk=nursery_id)

    if request.user != nursery.owner:
        return redirect("main:home")
    if request.method == 'POST':
        subscriptionForm = SubscriptionForm(request.POST)
        if subscriptionForm.is_valid():
            subscription = subscriptionForm.save(commit=False)  # Get the unsaved Activity instance
            subscription.nursery=nursery  # Set the nursery for this activity
            age_min = int(request.POST['age_min'])
            age_max = int(request.POST['age_max'])
            if 'min_age_years' in request.POST:
                age_min *= 12    # to be as months to better the search filltring later 
            if 'max_age_years' in request.POST:
                age_max *= 12 
            subscription.age_min=age_min    # age in months 
            subscription.age_max=age_max                           
            subscription.save()  
            messages.success(request, 'تم اضافه الباقه بنجاح!', 'alert-success')
            return redirect('nurseries:nursery_detail', nursery_id=nursery_id)
        else:
            for field, errors in subscriptionForm.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}", 'alert-danger')
                    return redirect('nurseries:nursery_detail', nursery_id=nursery_id)

    else:
        subscriptionForm = subscriptionForm()

    return render(request, 'nurseries/nursery_detail.html', {'subscriptionForm': subscriptionForm, 'nursery': nursery})


# class Review(models.Model):
#     nursery = models.ForeignKey(Nursery, on_delete=models.CASCADE, related_name='reviews')
#     parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='reviews')
#     rating = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
#     comment = models.TextField(blank=True)

def add_review(request, nursery_id):
    nursery = Nursery.objects.get(pk=nursery_id)
    if request.method == 'POST':
        # Check if the parent already has a review for this nursery
        existing_review = Review.objects.filter(nursery=nursery, parent=request.user.parent).exists()
        if existing_review:
           messages.error(request, 'لديك بالفعل تعليق لا يمكنك اضافه تعليق اخر ', 'alert-danger')
           return redirect('nurseries:nursery_detail', nursery_id=nursery_id)
        has_accepted_registration = Registration.objects.filter(
        subscription__nursery=nursery,
        child__parent=request.user.parent,
        status='accepted'
        ).exists()
        if has_accepted_registration:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.nursery = nursery
                review.parent = request.user.parent
                review.save()
                return redirect('nurseries:nursery_detail', nursery_id=nursery.id)
            else:
              for field, errors in review_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}", 'alert-danger')
        else:
          messages.error(request, '  ليس لديك اطفال فيه هذه الحضانه ', 'alert-danger')
          print(messages.error)
          return redirect('nurseries:nursery_detail', nursery_id=nursery.id)



    return render(request, 'nurseries/nursery_detail.html')
