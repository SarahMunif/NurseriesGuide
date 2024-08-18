from django.shortcuts import render , redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest, HttpResponse, Http404
from django.core.paginator import Paginator
from django.contrib import messages
from django.db import IntegrityError , transaction
from django.contrib.auth.models import User
from nurseries.models import Nursery
from .models import Parent
from .models import Child
from .forms import ChildForm


def add_child(request:HttpRequest):

    parent = Parent.objects.get(user=request.user)

    if request.method == 'POST':
        print("im here in add child")
        form = ChildForm(request.POST, request.FILES)
        if form.is_valid():
            child = form.save(commit=False)
            child.parent = parent
            child.save()
            messages.success(request, "تم إضافة الطفل بنجاح", "alert-success")
            return redirect('parents:parent_profile', user_id=request.user.id)
    else:
        form = ChildForm()

    return render(request, 'parents/profile.html')

def update_parent(request:HttpRequest):
    pass
def delete_child(request:HttpRequest):
    pass

def update_child(request:HttpRequest):
    pass


def signup_manager(request:HttpRequest):
    
    if request.method == "POST":

        try:
            with transaction.atomic():
                new_manager = User.objects.create_user(username=request.POST["username"],password=request.POST["password"],email=request.POST["email"], first_name=request.POST["first_name"], last_name=request.POST["last_name"],is_staff=True  )
                new_manager.save()

                login(request, new_manager)


            messages.success(request, "تم تسجيلك كمالك حضانة بنجاح ", "success")
            return redirect(request.GET.get("next", "/"))

        except IntegrityError as e:
            messages.error(request, "تم ادخال معلومات خاطئة ، ادخل  معلومات صحيحة", "danger")
            print(e)
        except Exception as e:
            messages.error(request, "حدث خطأ غير متوقع يرجى الحاولة مره اخرى", "danger")
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

    # user = User.objects.get(id=user_id)
    
    children = Child.objects.filter(parent=user_id)


    return render(request, 'parents/profile.html', {"children":children , "gender":Child.GenderChoices.choices})



