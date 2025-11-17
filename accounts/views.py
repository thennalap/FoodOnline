from django.http import HttpResponse
from django.shortcuts import redirect, render
from .forms import UserForm
from .models import User
from django.contrib import messages

# Create your views here.
def registerUser(request):
    if request.method=='POST':
        form=UserForm(request.POST)
        if form.is_valid():
            # create user using forms
            # password=form.cleaned_data['password']
            # user=form.save(commit=False)
            # user.role=User.CUSTOMER
            # user.set_password(password)      
            # user.save()

            # create user using create_user method
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            username=form.cleaned_data['username']
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            user=User.objects.create_user(first_name=first_name,last_name=last_name,username=username,email=email,password=password)
            user.role=User.CUSTOMER
            user.save() 
            messages.success(request,"Account Registered Successfully.")
            return redirect('registerUser')   # this is the name of the url pattern. which redirects in to that url
        
    else:
        form=UserForm()
    context={
        'form':form,
    }
    return render(request,'accounts/registerUser.html',context)
