from django.shortcuts import render,redirect
from . models import Order
from carts.models import CartItem
from .models import Order,Payment,OrderProduct
from .forms import OrderForm
import datetime
import json
from store.models import Product
from django.http import JsonResponse

def payments(request):
    body = json.loads(request.body)            #getting body json and storing
    order = Order.objects.get(user=request.user,is_ordered=False,order_number=body['orderID'])
    payment = Payment(
        user=request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],          #getting values from body and storing
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment =  payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price  = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.filter(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)        #newly generated id , we are targeting
        orderproduct.variations.set(product_variation)
        orderproduct.save()

        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    data ={                                            # we are sending this back to payments.html ->sendData function
        'order_number':order.order_number,
        'transID':payment.payment_id,
    }

    return JsonResponse(data)

def place_order(request,total=0,quantity=0):

    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address = form.cleaned_data['address']
            data.city = form.cleaned_data['city']
            data.country = form.cleaned_data['country']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')            #will provide current ip
            data.save()

            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d =  datetime.date(yr,mt,dt)

            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)                # data.id= order.id
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user,is_ordered=False,order_number=order_number)
            context = {
                'order':order,
                'cart_items':cart_items,
                'total':total,
                'tax':tax,
                'grand_total':grand_total,
            }
            return render(request,'orders/payments.html',context)
        else:
            return redirect('checkout')


def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')
    print(f"Received Order Number: {order_number}")
    print(f"Received Order Number: {transID}")
    try:
        order = Order.objects.get(order_number=order_number,is_ordered=True)
        order_products = OrderProduct.objects.filter(order_id=order.id)

        sub_total = 0
        for i in order_products:
            sub_total = i.product.price * i.quantity

        payment = Payment.objects.get(payment_id=transID)

        context = {
            "order":order,
            "order_products":order_products,
            "order_number":order.order_number,
            "transID":payment.payment_id,
            'payment':payment,
            'sub_total':sub_total,
        }
        return render(request,'orders/orders_complete.html',context)
    except(Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
