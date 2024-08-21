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

def update_parent(request: HttpRequest):
    # print(parent_id)
    if not request.user.is_authenticated:
        return redirect("main:home")  # Redirect non-authenticated users to home page

    # parent = get_object_or_404(Parent, pk=parent_id)

    if request.method == "POST":
        print("im here")
        try:
            with transaction.atomic():
                user:User = request.user

                user.first_name = request.POST["first_name"]
                user.last_name = request.POST["last_name"]
                user.email = request.POST["email"]
                user.username = request.POST["username"]
                user.save()

                parent:Parent = user.parent
                parent.phone_number = request.POST["phone_number"]
                parent.Work_number = request.POST["Work_number"]

                parent.save()

            messages.success(request, "تم تحديث البيانات بنجاح", 'alert-success')
        except Exception as e:
            messages.error(request, "تم إدخال معلومات خاطئة، أدخل معلومات صحيحة", 'alert-danger')
            print(e)
    
    return render(request, 'parents/profile.html', {'parent': parent})

def child_detail(request:HttpRequest):
    pass


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



def signup_manager(request:HttpRequest):
    
    if request.method == "POST":

        try:
            with transaction.atomic():
                new_manager = User.objects.create_user(username=request.POST["username"],password=request.POST["password"],email=request.POST["email"], first_name=request.POST["first_name"], last_name=request.POST["last_name"],is_staff=True  )
                new_manager.save()

                login(request, new_manager)


            messages.success(request, "تم تسجيلك كمالك حضانة بنجاح ", "alert-success")
            return redirect(request.GET.get("next", "/"))

        except IntegrityError as e:
            messages.error(request, "تم ادخال معلومات خاطئة ، ادخل  معلومات صحيحة", "alert-danger")
            print(e)
        except Exception as e:
            messages.error(request, "حدث خطأ غير متوقع يرجى الحاولة مره اخرى", "alert-danger")
            print(e)

    return render(request,"parents/sign_up_manager.html")


def signup_parent(request:HttpRequest):
    
    if request.method == "POST":

        try:
            with transaction.atomic():
                new_parent = User.objects.create_user(username=request.POST["username"],password=request.POST["password"],email=request.POST["email"], first_name=request.POST["first_name"], last_name=request.POST["last_name"])
                new_parent.save()
                profile = Parent(user=new_parent, Work_number=request.POST["Work_number"],phone_number=request.POST["phone_number"])
                profile.save()
                login(request, new_parent)


            messages.success(request, "تم تسجيلك كولي امر بنجاح ", "alert-success")
            return redirect(request.GET.get("next", "/"))
        
        except IntegrityError as e:
            messages.error(request, "تم ادخال معلومات خاطئة ، ادخل  معلومات صحيحة", "alert-danger")
            print(e)
        except Exception as e:
            messages.error(request, "حدث خطأ غير متوقع يرجى الحاولة مره اخرى", "alert-danger")
            print(e)

    return render(request,"parents/sign_up_parent.html")


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

def parent_profile(request:HttpRequest, user_id):

    
    parent = get_object_or_404(Parent, user=request.user)
    children = Child.objects.filter(parent=parent)


    return render(request, 'parents/profile.html', {"parent":parent ,"children":children,"gender": Child.GenderChoices.choices})




