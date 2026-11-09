def cart_and_wishlist_counts(request):
    cart = request.session.get('cart', {})
    wishlist = request.session.get('wishlist', [])
    
    # Total count of individual quantities in cart
    total_cart_items = sum(cart.values())
    total_wishlist_items = len(wishlist)

    return {
        'cart_count': total_cart_items,
        'wishlist_count': total_wishlist_items,
    }