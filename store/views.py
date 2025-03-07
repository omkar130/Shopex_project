from django.shortcuts import render
from .models import Product
from category.models import Category
from  carts.views import _cart_id
from carts.models import CartItem
from django.db.models import Q

def store(request, category_slug=None):
    categories=None
    products=None

    if category_slug !=None:
        categories = Category.objects.get(slug=category_slug)
        products = Product.objects.filter(category=categories,is_available=True)
        product_count = products.count()
    else:

        products = Product.objects.all().filter(is_available=True)
        product_count = products.count()

    context = {
        "products":products,
        "product_count":product_count,
    }
    return render(request,"store/store.html",context)


def product_detail(request,category_slug,product_slug):
    single_product = Product.objects.get(category__slug=category_slug,slug=product_slug)  # category__slug means Category.object.get(slug=category_slug)
    in_cart =  CartItem.objects.filter(cart__cart_id=_cart_id(request),product=single_product).exists()  # to check if current product available in cart or not

    context = {
        "single_product":single_product,
        "in_cart":in_cart,
    }
    return render(request,'store/product_detail.html',context)


def search(request):
    if 'keyword' in request.GET:
        keyword =  request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()

        context={
            "products":products,
            "product_count":product_count,
        }
        return render(request,'store/store.html',context)
