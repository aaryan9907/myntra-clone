from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import Product, Category
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import uuid

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

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    # Grab related products from the same category
    similar_products = Product.objects.filter(
        category=product.category
    ).exclude(pk=product.pk)[:5]

    context = {
        'product': product,
        'similar_products': similar_products,
        'sizes': ['S', 'M', 'L', 'XL', 'XXL'],
    }
    return render(request, 'product_detail.html', context)

# --- CART / BAG VIEWS ---

@require_POST
def add_to_bag(request, pk):
    product = get_object_or_404(Product, pk=pk)
    size = request.POST.get('size')
    
    if not size:
        return JsonResponse({'status': 'error', 'message': 'Please select a size'}, status=400)
    
    cart = request.session.get('cart', {})
    # Key items by product_id and size (e.g., "12-M")
    cart_key = f"{product.id}-{size}"
    cart[cart_key] = cart.get(cart_key, 0) + 1
    
    request.session['cart'] = cart
    request.session.modified = True
    
    total_count = sum(cart.values())
    return JsonResponse({'status': 'success', 'cart_count': total_count})


def bag_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_mrp = 0
    total_discounted = 0

    for cart_key, quantity in cart.items():
        product_id, size = cart_key.split('-')
        try:
            product = Product.objects.get(id=product_id)
            item_mrp_total = int(round(product.price)) * quantity
            item_discounted_total = product.discounted_price * quantity

            total_mrp += item_mrp_total
            total_discounted += item_discounted_total

            cart_items.append({
                'cart_key': cart_key,
                'product': product,
                'size': size,
                'quantity': quantity,
                'item_mrp_total': item_mrp_total,
                'item_discounted_total': item_discounted_total,
            })
        except Product.DoesNotExist:
            continue

    discount_on_mrp = total_mrp - total_discounted
    convenience_fee = 20 if cart_items else 0
    final_amount = total_discounted + convenience_fee

    context = {
        'cart_items': cart_items,
        'total_mrp': total_mrp,
        'discount_on_mrp': discount_on_mrp,
        'convenience_fee': convenience_fee,
        'final_amount': final_amount,
    }
    return render(request, 'bag.html', context)


@require_POST
def remove_from_bag(request, cart_key):
    cart = request.session.get('cart', {})
    if cart_key in cart:
        del cart[cart_key]
        request.session['cart'] = cart
        request.session.modified = True
    return redirect('bag')


# --- WISHLIST VIEWS ---

@require_POST
def toggle_wishlist(request, pk):
    product = get_object_or_404(Product, pk=pk)
    wishlist = request.session.get('wishlist', [])

    if product.id in wishlist:
        wishlist.remove(product.id)
        action = 'removed'
    else:
        wishlist.append(product.id)
        action = 'added'

    request.session['wishlist'] = wishlist
    request.session.modified = True
    return JsonResponse({'status': 'success', 'action': action, 'wishlist_count': len(wishlist)})


def wishlist_view(request):
    wishlist_ids = request.session.get('wishlist', [])
    products = Product.objects.filter(id__in=wishlist_ids)
    return render(request, 'wishlist.html', {'products': products})

@require_POST
def move_wishlist_to_bag(request, pk):
    product = get_object_or_404(Product, pk=pk)
    size = request.POST.get('size', 'M')
    
    # 1. Add to Bag
    cart = request.session.get('cart', {})
    cart_key = f"{product.id}-{size}"
    cart[cart_key] = cart.get(cart_key, 0) + 1
    request.session['cart'] = cart
    
    # 2. Remove from Wishlist
    wishlist = request.session.get('wishlist', [])
    if product.id in wishlist:
        wishlist.remove(product.id)
    request.session['wishlist'] = wishlist
    
    request.session.modified = True
    
    return JsonResponse({
        'status': 'success',
        'cart_count': sum(cart.values()),
        'wishlist_count': len(wishlist),
    })

@require_POST
def update_bag_quantity(request, cart_key):
    try:
        new_qty = int(request.POST.get('quantity', 1))
        if new_qty < 1:
            new_qty = 1
    except ValueError:
        new_qty = 1

    cart = request.session.get('cart', {})
    if cart_key in cart:
        cart[cart_key] = new_qty
        request.session['cart'] = cart
        request.session.modified = True

    return redirect('bag')


@require_POST
def move_bag_to_wishlist(request, cart_key):
    cart = request.session.get('cart', {})
    wishlist = request.session.get('wishlist', [])

    if cart_key in cart:
        product_id, _ = cart_key.split('-')
        product_id = int(product_id)

        # Remove from cart
        del cart[cart_key]
        request.session['cart'] = cart

        # Add to wishlist if not already present
        if product_id not in wishlist:
            wishlist.append(product_id)
            request.session['wishlist'] = wishlist

        request.session.modified = True

    return redirect('bag')


def place_order(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('bag')

    # Generate a realistic mock Myntra Order ID
    order_id = f"MYN-{uuid.uuid4().hex[:8].upper()}"

    # Calculate final summary totals before clearing
    cart_items = []
    total_amount = 0
    for cart_key, quantity in cart.items():
        product_id, size = cart_key.split('-')
        try:
            prod = Product.objects.get(id=product_id)
            item_total = prod.discounted_price * quantity
            total_amount += item_total
            cart_items.append({
                'product': prod,
                'size': size,
                'quantity': quantity,
                'total_price': item_total,
            })
        except Product.DoesNotExist:
            continue

    total_amount += 20  # Convenience fee

    # Clear shopping bag
    request.session['cart'] = {}
    request.session.modified = True

    context = {
        'order_id': order_id,
        'order_items': cart_items,
        'total_amount': total_amount,
    }
    return render(request, 'order_success.html', context)