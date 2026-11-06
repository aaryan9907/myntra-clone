from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Product, Category
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required

def show(request):
    all_categories = Category.objects.all()
    products = Product.objects.all()

    # Distribute categories by gender for the hover dropdown menus
    men_categories = all_categories.filter(gender='men')
    women_categories = all_categories.filter(gender='women')
    kids_categories = all_categories.filter(gender='kids')

    # Available brands for filter checkboxes
    available_brands = Product.objects.values_list('brand', flat=True).distinct().order_by('brand')

    # Check active filters
    gender_filter = request.GET.get('gender')
    selected_categories = request.GET.getlist('category')
    selected_brands = request.GET.getlist('brand')
    query = request.GET.get('q')
    sort_by = request.GET.get('sort', 'new')

    # Is the user currently in a filtered/listing mode?
    is_filtered_view = bool(gender_filter or selected_categories or selected_brands or query)

    # 1. Gender Filter
    filtered_categories = all_categories
    if gender_filter:
        products = products.filter(category__gender=gender_filter.lower())
        filtered_categories = all_categories.filter(gender=gender_filter.lower())

    # 2. Category Slugs Filter
    if selected_categories:
        products = products.filter(category__slug__in=selected_categories)

    # 3. Brand Filter
    if selected_brands:
        products = products.filter(brand__in=selected_brands)

    # 4. Search Filter
    if query:
        products = products.filter(
            Q(title__icontains=query) | Q(brand__icontains=query) | Q(description__icontains=query)
        )

    # 5. Sorting
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'rating':
        products = products.order_by('-rating', '-rating_count')
    elif sort_by == 'discount':
        products = products.order_by('-discount_percentage')
    else:
        products = products.order_by('-created_at')

    context = {
        'products': products,
        'categories': filtered_categories,
        'men_categories': men_categories,
        'women_categories': women_categories,
        'kids_categories': kids_categories,
        'available_brands': available_brands,
        'selected_gender': gender_filter or '',
        'selected_categories': selected_categories,
        'selected_brands': selected_brands,
        'selected_sort': sort_by,
        'query': query or '',
        'total_count': products.count(),
        'is_filtered_view': is_filtered_view,
    }
    return render(request, 'home.html', context)

def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()

    return render(request, 'auth/login.html', {'form': form})

def user_signup(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'auth/signup.html', {'form': form})

def user_logout(request):
    if request.method == 'POST':
        logout(request)
    return redirect('home')

@login_required(login_url='login')
def profile_view(request):
    return render(request, 'profile.html', {'user': request.user})