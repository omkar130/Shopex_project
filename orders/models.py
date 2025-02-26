from django.db import models
from accounts.models import Account
from store.models import Product, Variation

class Payment(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id


class Order(models.Model):
    STATUS = (
        ('New','New'),
        ('Accepted','Accepted'),
        ('Completed','Completed'),
        ('Cancelled','Cancelled'),
    )

    user = models.ForeignKey(Account,on_delete=models.SET_NULL,null=True)
    payment = models.ForeignKey(Payment,on_delete=models.SET_NULL,blank=True,null=True)
    order_number = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    order_total = models.FloatField()
    tax = models.FloatField(default=0)
    status = models.CharField(max_length=50,choices=STATUS,default='New')
    ip = models.CharField(max_length=100,blank=True)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.first_name

class OrderProduct(models.Model):
        user = models.ForeignKey(Account,on_delete=models.CASCADE)                           # if parent delete make child delete
        payment = models.ForeignKey(Payment,on_delete=models.SET_NULL,blank=True,null=True)   # if parent get's delete make child null
        order = models.ForeignKey(Order,on_delete=models.CASCADE)
        product = models.ForeignKey(Product,on_delete=models.CASCADE)
        variation = models.ManyToManyField(Variation,blank=True)
        quantity = models.IntegerField()
        product_price = models.FloatField()
        ordered = models.BooleanField(default=False)
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)

        def __str__(self):
            return self.product.product_name
