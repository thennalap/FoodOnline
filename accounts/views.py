from django.http import HttpResponse
from django.shortcuts import redirect, render
from .utils import detectUser
from .forms import UserForm
from .models import User, UserProfile
from django.contrib import messages,auth
from vendor.forms import VendorForm
from django.contrib.auth.decorators import login_required,user_passes_test
from django.core.exceptions import PermissionDenied

#restrict the vendor from accessing the customer pages
def check_role_vendor(user):
    if user.role==1:
        return True
    else:
        raise PermissionDenied

#restrict the customer from accessing the vendor pages
def check_role_customer(user):
    if user.role==2:
        return True
    else:
        raise PermissionDenied

# Create your views here.
def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request,"Already Logged In.")
        return redirect('myAccount')
    elif request.method=='POST':
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
    if request.user.is_authenticated:
        messages.warning(request,"Already Logged In.")
        return redirect('myAccount')
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


def login(request):
    if request.user.is_authenticated:
        messages.warning(request,"Already Logged In.")
        return redirect('myAccount')
    elif request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        user=auth.authenticate(email=email,password=password)
        print(user,"userrrrrrrrrrrrrrrrttttttttttttt")

        if user is not None:
            print(user,"userrrrrrrrrrrrrrrr")
            auth.login(request,user)
            messages.success(request,"You are now logged in!")
            return redirect('myAccount')
        else:
            messages.error(request,"Invalid Login Credentials. ")
            return redirect('login')


    return render(request,'accounts/login.html')

def logout(request):
    auth.logout(request)
    messages.info(request,"You are Logged Out! ")
    return redirect('login')


@login_required(login_url='login')
def myAccount(request):
    user=request.user
    redirectUrl=detectUser(user)
    return redirect(redirectUrl)


@login_required(login_url='login')
@user_passes_test(check_role_customer)
def customerDashboard(request):
    return render(request,'accounts/customerDashboard.html')


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    return render(request,'accounts/vendorDashboard.html')


