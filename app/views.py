from django.shortcuts import render
from .models import Product, Category

def show(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    # Filter by gender (e.g., /?gender=men)
    gender_filter = request.GET.get('gender')
    if gender_filter:
        products = products.filter(category__gender=gender_filter.lower())

    # Filter by category slug (e.g., /?category=t-shirts)
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)

    # Sorting logic (e.g., /?sort=price_low)
    sort_by = request.GET.get('sort')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'rating':
        products = products.order_by('-rating')
    else:
        products = products.order_by('-created_at')

    context = {
        'products': products,
        'categories': categories,
        'selected_gender': gender_filter,
        'selected_category': category_slug,
        'selected_sort': sort_by,
    }
    return render(request, 'home.html', context)