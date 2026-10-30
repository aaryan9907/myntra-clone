from django.shortcuts import render
from .models import Product, Category

def show(request):
    products = Product.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'home.html', context)