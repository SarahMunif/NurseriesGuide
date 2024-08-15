from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Registration







@login_required
def registration_create(request):
    pass





@login_required
def registration_list(request):
    pass




@login_required
def registration_detail(request, pk):
    pass





@login_required
def registration_update_status(request, pk):
    registration = get_object_or_404(Registration, pk=pk)
    pass
