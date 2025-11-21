from django.http import HttpResponse
from django.shortcuts import redirect, render
from .utils import detectUser,send_verification_email
from .forms import UserForm
from .models import User, UserProfile
from django.contrib import messages,auth
from vendor.forms import VendorForm
from django.contrib.auth.decorators import login_required,user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator


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

            # Send Verification Email
            mail_subject='Please Activate Your Account'
            email_template='accounts/emails/account_verification_email.html'
            send_verification_email(request,user,mail_subject,email_template)
            messages.success(request,"Account created successfully! Please check your email to activate your account before logging in. ")
            return redirect('login')   # this is the name of the url pattern. which redirects in to that url
        
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

            # Send Verification Email
            mail_subject='Please Activate Your Account'
            email_template='accounts/emails/account_verification_email.html'
            send_verification_email(request,user,mail_subject,email_template)
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


def activate(request,uidb64,token):
    # Activate the user by setting the is_active field True
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=User._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        user=None

    if user is not None and default_token_generator.check_token(user,token):
        user.is_active=True
        user.save()
        messages.success(request,"Yaay!! Your Account is Activated.")
        return redirect('login')
    else:
        messages.error(request,"Invalid Activation Link")
        return redirect('login')



def login(request):
    if request.user.is_authenticated:
        messages.warning(request,"Already Logged In.")
        return redirect('myAccount')
    elif request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        user=auth.authenticate(email=email,password=password)        

        if user is not None:            
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

def forgotPassword(request):
    if request.method == 'POST':
        email=request.POST['email']

        if User.objects.filter(email=email).exists():
            user=User.objects.get(email__exact=email)
            #Send reset password email
            mail_subject="Reset Your Password"
            email_template="accounts/emails/reset_password_email.html"
            send_verification_email(request,user,mail_subject,email_template)
            messages.success(request,"Password reset link has been sent to your Email Address.")
            return redirect('login')
        else:
            messages.success(request,"Account doesnot exists!!")
            return redirect('forgotPassword')
    return render(request,'accounts/forgotPassword.html')

def resetPasswordValidate(request,uidb64,token):
    # Validate the User by decoding the token coming from the Email and uid
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=User._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        user=None

    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid']=uid
        messages.info(request,'Please reset your password')
        return redirect('resetPassword')

    else:
        messages.error(request,"Link has been expired")
        return redirect('forgotPassword')


def resetPassword(request):
    if request.method == 'POST':
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']
        if password==confirm_password:
            # take primary key that saved inside the session during the time of validation.
            pk=request.session.get('uid')
            user=User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active=True
            user.save()
            messages.success(request,"Password Reset Successfully")
            return redirect('login')
        else:
            messages.error(request,"Passwords do not match")
            return redirect('resetPassword')
    return render(request,'accounts/resetPassword.html')


