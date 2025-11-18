from django.http import HttpResponse
from django.shortcuts import redirect, render
from .forms import UserForm
from .models import User, UserProfile
from django.contrib import messages
from vendor.forms import VendorForm

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


def registerVendor(request):
    if request.method =='POST':
        form=UserForm(request.POST)
        v_form=VendorForm(request.POST,request.FILES)
        if form.is_valid() and v_form.is_valid():
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            username=form.cleaned_data['username']
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            user=User.objects.create_user(first_name=first_name,last_name=last_name,username=username,email=email,password=password)
            user.role=User.VENDOR
            user.save() 

            vendor=v_form.save(commit=False)
            vendor.user=user
            userprofile=UserProfile.objects.get(user=user)
            vendor.userprofile=userprofile
            vendor.save()
            messages.success(request,"Your account has been registered successfully! Please wait for the approval.")
            return redirect('registerVendor')
        else:
            print("Invalid   form")
            print(form.errors)
    else:
        # It will be a get request...
        form=UserForm()
        v_form=VendorForm()
    context={   
        'form':form,
        'v_form':v_form
    }
    return render(request,'accounts/registerVendor.html',context)

