from django.shortcuts import render,redirect
from django.http import HttpRequest,HttpResponse
from .forms import NurseryForm
from django.contrib import messages 
from nurseries.models import Activity,City,Neighborhood,Nursery,Gallery,Staff
from django.core.paginator import Paginator

# Create your views here.

def nurseries_view(request:HttpRequest):
    pass

def add_nurseries(request:HttpRequest):
    pass

def delete_nursery(request:HttpRequest):
    pass
def update_nursery(request:HttpRequest):
    pass

def detail_nursery(request:HttpRequest):
    pass



def add_activity(request:HttpRequest):
    pass

def delete_activity(request:HttpRequest):
    pass

def update_activity(request:HttpRequest):
    pass




