from django.shortcuts import render , redirect ,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest, HttpResponse, Http404
from django.core.paginator import Paginator
from django.contrib import messages
from django.db import IntegrityError , transaction
from django.contrib.auth.models import User
from nurseries.models import Nursery
from .models import Parent
from .models import Child
from .forms import ChildForm ,ParentForm
from registrations.models import Registration
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, EmailValidator
import re 

def signup_parent(request: HttpRequest):
    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        work_number = request.POST.get("Work_number")
        
        # Server-side validation
        error_message = None
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            error_message = "اسم المستخدم موجود مسبقًا. يرجى اختيار اسم مستخدم آخر."
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            error_message = "البريد الإلكتروني مستخدم مسبقًا. يرجى استخدام بريد إلكتروني آخر."
        
        # Validate username (only alphanumeric characters and underscores)
        if not error_message and (not username or not username.isalnum()):
            error_message = "اسم المستخدم يجب أن يحتوي فقط على أحرف إنجليزية وأرقام."
        
        # Validate first and last names (Arabic and English letters)
        name_regex = r'^[a-zA-Z\u0621-\u064A\u066E-\u066F]+$'
        if not error_message and not re.match(name_regex, first_name):
            error_message = "الاسم الأول يجب أن يحتوي فقط على أحرف عربية أو إنجليزية."
        elif not error_message and not re.match(name_regex, last_name):
            error_message = "الاسم الأخير يجب أن يحتوي فقط على أحرف عربية أو إنجليزية."

        # Validate password length and content
        if not error_message and len(password) < 8:
            error_message = "يجب أن تحتوي كلمة المرور على ٨ أحرف أو أرقام على الأقل."
        elif not error_message and not re.match(r'^(?=.*[0-9])(?=.*[a-zA-Z]).{8,}$', password):
            error_message = "يجب أن تحتوي كلمة المرور على أحرف وأرقام."
        elif not error_message and password != confirm_password:
            error_message = "كلمة المرور غير متطابقة."
        
        # Validate email format and domain
        if not error_message:
            email_validator = EmailValidator()
            allowed_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com']
            try:
                email_validator(email)
                domain = email.split('@')[-1]
                if domain not in allowed_domains:
                    error_message = "يجب أن يكون البريد الإلكتروني صحيحا وضمن الايميلات المسموح تسجيلها (gmail, hotmail, yahoo, outlook, icloud)."
            except ValidationError:
                error_message = "البريد الإلكتروني غير صحيح."
        
        # Validate phone numbers
        if not error_message:
            phone_regex = r'^05[0-9]{8}$'
            phone_validator = RegexValidator(phone_regex, message="رقم الهاتف يجب أن يبدأ بـ '05' ويليه 8 أرقام.")
            try:
                phone_validator(phone_number)
                phone_validator(work_number)
            except ValidationError:
                error_message = "رقم الهاتف أو رقم هاتف العمل غير صحيح."
        
        if error_message:
            # Pass the current POST data back to the template to preserve user input
            return render(request, "parents/sign_up_parent.html", {
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone_number": phone_number,
                "work_number": work_number,
                "password":password,
                "confirm_password":confirm_password,
                "error_message": error_message,
            })

        # If no validation errors, proceed to save user and profile
        try:
            with transaction.atomic():
                new_parent = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                )
                profile = Parent(user=new_parent, Work_number=work_number, phone_number=phone_number)
                profile.save()
                login(request, new_parent)

            messages.success(request, "تم تسجيلك كولي امر بنجاح ", "alert-success")
            return redirect(request.GET.get("next", "/"))

        except IntegrityError:
            messages.error(request, "تم ادخال معلومات خاطئة ، ادخل  معلومات صحيحة", "alert-danger")
        except Exception as e:
            messages.error(request, "حدث خطأ غير متوقع يرجى المحاولة مرة أخرى", "alert-danger")
            print(e)

    return render(request, "parents/sign_up_parent.html")


def requests_status(request):
    if not request.user.is_authenticated or request.user.is_superuser or request.user.is_staff:
        return redirect("main:home")

    try:
        parent_obj = Parent.objects.get(user=request.user)
    except Parent.DoesNotExist:
        # Handle the case where the parent object does not exist
        return redirect("main:home")

    # Get all children related to the parent
    children = Child.objects.filter(parent=parent_obj)

    # Get all registration requests for the children
    registration_requests = Registration.objects.filter(child__in=children)

    context = {
        'status_choices': Registration.STATUS_CHOICES,
        'children': children,
        'registration_requests': registration_requests,
    }

    return render(request, 'parents/request_status.html', context)

def add_child(request:HttpRequest):

    if not request.user.is_authenticated:
        return redirect("main:home")  # Redirect non-authenticated users to home page

    parent = Parent.objects.get(user=request.user)

    if request.method == "POST":
        form = ChildForm(request.POST, request.FILES)
        if form.is_valid():
            child = form.save(commit=False)
            child.parent = parent 
            child.save()    
            messages.success(request, "تم إضافة الطفل بنجاح", 'alert-success')

        else:
            print(form.errors)
            messages.error(request,  "تم ادخال معلومات خاطئة ، ادخل  معلومات صحيحة", 'alert-danger')
        return redirect(request.GET.get("next", "/"))

    return render(request, 'parents/profile.html', {"gender": Child.GenderChoices.choices})

def update_user(request: HttpRequest):
    if not request.user.is_authenticated:
        return redirect("main:home")  # Redirect non-authenticated users to home page

    if request.method == "POST":
        try:
            with transaction.atomic():
                user:User = request.user

                user.first_name = request.POST["first_name"]
                user.last_name = request.POST["last_name"]
                user.email = request.POST["email"]
                user.username = request.POST["username"]
                user.save()
                if not (request.user.is_superuser or request.user.is_staff ):

                    if "phone_number" or "Work_number" in request.POST:
                        parent:Parent = user.parent
                        parent.phone_number = request.POST["phone_number"]
                        parent.Work_number = request.POST["Work_number"]
                        parent.save()

            messages.success(request, "تم تحديث البيانات بنجاح", 'alert-success')

        except Exception as e:
            messages.error(request, "تم إدخال معلومات خاطئة، أدخل معلومات صحيحة", 'alert-danger')
            print("error",e)
        return redirect(request.GET.get("next", "/"))

def delete_child(request:HttpRequest,child_id):

    if not request.user.is_authenticated:
        return redirect("main:home")  # Redirect non-authenticated users to home page

    child = Child.objects.get(pk=child_id)

    if child.delete():
        messages.success(request, f'بنجاح{child.first_name}تم ازالة معلومات ',"alert-success")
    
    else:
        messages.error(request, f"{child.first_name} لم نتمكن من ازالة معلومات","alert-danger")    

    return redirect(request.GET.get("next", "/"))


def update_child(request:HttpRequest,child_id):

    if not request.user.is_authenticated:
        return redirect("main:home")  # Redirect non-authenticated users to home page

    # parent = Parent.objects.get(user=request.user)
    child = Child.objects.get(pk=child_id)

    if request.method == "POST":
        form = ChildForm(request.POST, request.FILES, instance=child)
        if form.is_valid():
            form.save()       
            messages.success(request, "تم إضافة الطفل بنجاح", 'alert-success')
        else:
            print(form.errors)
            messages.error(request,  "تم ادخال معلومات خاطئة ، ادخل  معلومات صحيحة", 'alert-danger')
        return redirect(request.GET.get("next", "/"))

    return render(request, 'parents/profile.html', {"gender": Child.GenderChoices.choices})

def signup_manager(request: HttpRequest):
    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        email = request.POST.get("email")
        
        # Server-side validation
        error_message = None

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            error_message = "اسم المستخدم موجود مسبقًا. يرجى اختيار اسم مستخدم آخر."
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            error_message = "البريد الإلكتروني مستخدم مسبقًا. يرجى استخدام بريد إلكتروني آخر."
        
        # Validate username (only alphanumeric characters)
        if not error_message and (not username or not username.isalnum()):
            error_message = "اسم المستخدم يجب أن يحتوي فقط على أحرف إنجليزية وأرقام."
        
        # Validate first and last names (Arabic and English letters)
        name_regex = r'^[a-zA-Z\u0621-\u064A\u066E-\u066F]+$'
        if not error_message and not re.match(name_regex, first_name):
            error_message = "الاسم الأول يجب أن يحتوي فقط على أحرف عربية أو إنجليزية."
        elif not error_message and not re.match(name_regex, last_name):
            error_message = "الاسم الأخير يجب أن يحتوي فقط على أحرف عربية أو إنجليزية."

        # Validate password length and content
        if not error_message and len(password) < 8:
            error_message = "يجب أن تحتوي كلمة المرور على ٨ أحرف أو أرقام على الأقل."
        elif not error_message and not re.match(r'^(?=.*[0-9])(?=.*[a-zA-Z]).{8,}$', password):
            error_message = "يجب أن تحتوي كلمة المرور على أحرف وأرقام."
        elif not error_message and password != confirm_password:
            error_message = "كلمة المرور غير متطابقة."
        
        # Validate email format and domain
        if not error_message:
            email_validator = EmailValidator()
            allowed_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com']
            try:
                email_validator(email)
                domain = email.split('@')[-1]
                if domain not in allowed_domains:
                    error_message = "يجب أن يكون البريد الإلكتروني صحيحا وضمن الايميلات المسموح تسجيلها (gmail, hotmail, yahoo, outlook, icloud)."
            except ValidationError:
                error_message = "البريد الإلكتروني غير صحيح."
        
        if error_message:
            # Pass the current POST data back to the template to preserve user input
            return render(request, "parents/sign_up_manager.html", {
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "password":password,
                "confirm_password":confirm_password,
                "email": email,
                "error_message": error_message,
            })

        # If no validation errors, proceed to save user
        try:
            with transaction.atomic():
                new_manager = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    is_staff=True  # Set manager role
                )
                new_manager.save()
                login(request, new_manager)

            messages.success(request, "تم تسجيلك كمالك حضانة بنجاح ", "alert-success")
            return redirect(request.GET.get("next", "/"))

        except IntegrityError:
            messages.error(request, "تم ادخال معلومات خاطئة ، ادخل  معلومات صحيحة", "alert-danger")
        except Exception as e:
            messages.error(request, "حدث خطأ غير متوقع يرجى المحاولة مرة أخرى", "alert-danger")
            print(e)

    return render(request, "parents/sign_up_manager.html")


def signin(request:HttpRequest):

    if request.method == "POST":
        #checking user credentials
        user = authenticate(request, username=request.POST["username"], password=request.POST["password"])
        print(user)
        if user:
            #login the user
            login(request, user)
            messages.success(request, "تم تسجيل الدخول بنجاح", "alert-success")
            return redirect(request.GET.get("next", "/"))
        else:
            messages.error(request, "معلومات تسجيل دخول خاطئة ،تأكد من صحة المعلومات ", "alert-danger")



    return render(request, "parents/sign_in.html")


def log_out(request: HttpRequest):

    logout(request)
    messages.success(request, "تم تسجيل الخروج بنجاح", "alert-warning")

    return redirect(request.GET.get("next", "/"))

def parent_profile(request:HttpRequest):

    if not request.user.is_authenticated or request.user.is_staff or request.user.is_superuser :
        return redirect(request.GET.get("next", "/"))
    
    parent = request.user.parent
    children = Child.objects.filter(parent=parent)


    return render(request, 'parents/parent_profile.html', {"parent":parent ,"children":children,"gender": Child.GenderChoices.choices})

    




