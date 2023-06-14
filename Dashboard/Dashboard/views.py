from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import IntegrityError
import os
import datetime


@csrf_exempt
def login(request):
   if request.method == 'POST':
      username = request.POST['username']
      password = request.POST['password']
      user = auth.authenticate(username=username, password=password)
      if user is not None:
         if user.is_active:
            auth.login(request, user)
         return redirect(reverse('PlaylogList'))
      else:
         error="username or password is incorrect"
         return render(request,'index.html',{'error':error})
   else:
      return render(request, 'index.html')


@csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST['username']
            password = request.POST['password']
            confirm_password = request.POST['confirm-password']

            # Validate form data
            if password != confirm_password:
                raise ValueError('Passwords do not match')

            # Create new user
            user = User.objects.create_user(username=name, password=password)
            user.save()

            # Log the user in
            user = auth.authenticate(username=name, password=password)
            if user is not None:
                auth.login(request, user)
                return redirect(reverse('PlaylogList'))
            else:
                raise ValueError('Authentication failed')

        except (IntegrityError, ValueError) as e:
            return render(request, 'signup.html', {'error': 'User Already Exist'})
        except Exception:
            error = 'An error occurred. Please try again later.'
            return render(request, 'signup.html', {'error': error})

    return render(request, 'signup.html')


@login_required
@csrf_exempt
def signout(request):
   auth.logout(request)
   return render(request, 'index.html')
