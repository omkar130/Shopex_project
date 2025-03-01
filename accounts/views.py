from django.shortcuts import render,redirect
from .forms import RegistrationForm, UserForm,UserProfileForm
from .models import Account,UserProfile
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from carts.views import _cart_id
from carts.models import Cart,CartItem
import requests
from orders.models import Order,OrderProduct

def register(request):
    if request.method == 'POST':
        form =  RegistrationForm(request.POST)       #getting data entered by user
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user=Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password)
            user.phone_number = phone_number
            user.save()

            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_pic = 'default/img_avatar.png'
            profile.save()

            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),                #encoding user's primary key
                'token':default_token_generator.make_token(user),                 #to generate token
            })

            to_email = email
            send_mail = EmailMessage(mail_subject,message,to=[to_email])
            send_mail.send()

            return redirect('/accounts/login/?command=verification&email='+email)
    else:
        form = RegistrationForm()
    context ={
        "form":form,
    }
    return render(request,"accounts/register.html",context)


def login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        user= auth.authenticate(email=email,password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)


                    #getting cart items of cart
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    #getting cart items of user
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        ex_var_list =   item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    # get common variation by checking cart(cart_items) and user(cart_items)
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)     #getting actual location of variation
                            item_id = id[index]               #getting id of it
                            item = CartItem.objects.get(id=item_id)
                            item.quantity +=1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user=user
                                item.save()
            except:
               pass
            auth.login(request,user)
            messages.success(request,'You are now logged in')
            url = request.META.get('HTTP_REFERER')          #gives url of previous page
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))         # dict will store string like key:value e.g next : /cart/checkout
                if 'next' in params:
                    nextPage = params['next']                                 # params['next'], you will get  /cart/checkout
                    return redirect(nextPage)
            except:
                return redirect('dashboard')

        else:
            messages.error(request,'Invalid Login Credentials')
            return redirect('login')
    return render(request,'accounts/login.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request,'You are logged out')
    return redirect('login')


def activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()     #decoding users primary key
        user = Account._default_manager.get(pk=uid)      #with primary key getting user
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        user.is_active=True
        user.save()
        message.success(request,'Congratulations!, Your account is activated')
        return redirect('login')
    else:
        message.error(request,'Invalid activation link')
        return redirect('register')

@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id,is_ordered=True)
    orders_count = orders.count()
    userprofile = UserProfile.objects.get(user=request.user.id)
    context = {
        "orders_count":orders_count,
        "userprofile":userprofile,
    }
    return render(request,"accounts/dashboard.html",context)


def my_orders(request):
    orders = Order.objects.filter(user=request.user,is_ordered=True).order_by('-created_at')
    context = {
     "orders":orders
    }
    return render(request,"accounts/my_orders.html",context)


def edit_profile(request):
    userprofile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST,instance=request.user)                 #using instance we are updating profile
        profile_form = UserProfileForm(request.POST,request.FILES,instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,'Profile has been updated')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)

    context = {
         "user_form":user_form,
         "profile_form":profile_form,
         "userprofile":userprofile,
    }

    return render(request,'accounts/edit_profile.html',context)

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact = request.user.username)
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request,'Password Updated Successfully')
                return redirect('change_password')
            else:
                messages.error(request,'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request,'password does not match')
            return redirect('change_password')
    return render(request,"accounts/change_password.html")

@login_required(login_url='login')
def order_detail(request,order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    sub_total = 0
    for i in order_detail:
        sub_total += i.product_price * i.quantity
    context = {
        'order_detail':order_detail,
        'order':order,
        'sub_total':sub_total,
    }
    return render(request,'accounts/order_detail.html',context)
