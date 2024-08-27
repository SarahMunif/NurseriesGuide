from django.shortcuts import render
from django.contrib import messages 
from django.shortcuts import render,redirect
from django.db.models import Count,Min,Max
from nurseries.models import Nursery,City,Activity,Gallery
from parents.models import Parent

from .models import Contact,Web_Review
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib import messages
from .forms import Web_ReviewForm
def home(request):
     
    nurseries = Nursery.objects.filter(status='verified')[0:3]# only verfied nursires can be displayed
    nurseries_count = Nursery.objects.count()
    cities_count = City.objects.count()
    parents_count = Parent.objects.count()
    reviews=Web_Review.objects.all()
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


    return render(request, 'main/home.html',{"nurseries_count":nurseries_count,"cities_count":cities_count,"parents_count":parents_count,
                                             "nurseries":nurseries,
                                             "reviews":reviews})


def about_us(request):
    return render(request, 'main/about_us.html')


def terms_of_use(request):
    return render(request, 'main/terms_of_use.html')

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


def contact_view(request):
    
    if request.method == "POST":
        print(f'this')

        contact = Contact(first_name=request.POST["first_name"],last_name=request.POST["last_name"], email=request.POST["email"], message=request.POST["message"])
        contact.save()

        #send confirmation email
        send_to = settings.EMAIL_HOST_USER
        print(f'this{send_to}')
        content_html = render_to_string("main/mail/confirmation.html",{"contact":contact})
        email_message = EmailMessage("لديك رسالة جديدة",content_html, settings.EMAIL_HOST_USER, [send_to])
        email_message.content_subtype = "html"
        email_message.send()
        messages.success(request, 'تم استلام رسالتك شكرا لتواصلك معنا',"alert-success")
        return redirect('main:contact_view') 
    return render(request, 'main/contact_us.html' )


def add_review(request):
    if request.method == 'POST':
        existing_review = Web_Review.objects.filter(parent=request.user.parent).exists()
        if existing_review:
              messages.error(request, 'لديك بالفعل تعليق لا يمكنك اضافه تعليق اخر ', 'alert-danger')
              return redirect('main:home')
        review_form = Web_ReviewForm(request.POST)
        if review_form.is_valid():
                review = review_form.save(commit=False)
                review.parent = request.user.parent  
                review.save()
                return redirect('main:home')
        else:
              for field, errors in review_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}", 'alert-danger')
    else:
          messages.error(request, ' ', 'alert-danger')
          print(messages.error)
          return redirect('main:home')

    return render(request, 'main/home.html')