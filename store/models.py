from django.db import models
from category.models import Category
from django.urls import reverse


class Product(models.Model):
    product_name = models.CharField(max_length=200,unique=True)
    slug         = models.SlugField(max_length=200,unique=True)
    description  = models.TextField(max_length=200,unique=True)
    price        = models.IntegerField()
    images       = models.ImageField(upload_to='photos/products')
    stock        = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category     = models.ForeignKey(Category,on_delete=models.CASCADE)
    created_date =  models.DateTimeField(auto_now_add=True)   #auto_now_add - saves time of object creation
    modified_date =  models.DateTimeField(auto_now=True)      #auto_now - saves everytime when object gets modified


    def __str__(self):
        return self.product_name

    def get_url(self):
        return reverse('product_detail',args=[self.category.slug, self.slug])
