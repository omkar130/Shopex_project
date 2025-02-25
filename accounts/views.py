from django.shortcuts import render,redirect
from .forms import RegistrationForm
from .models import Account
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

def dashboard(request):
    return render(request,"accounts/dashboard.html")
