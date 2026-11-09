from django.urls import path
from . import views

urlpatterns = [
    path('', views.show, name='home'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    
    # Bag
    path('bag/', views.bag_view, name='bag'),
    path('bag/add/<int:pk>/', views.add_to_bag, name='add_to_bag'),
    path('bag/remove/<str:cart_key>/', views.remove_from_bag, name='remove_from_bag'),
    path('bag/update-qty/<str:cart_key>/', views.update_bag_quantity, name='update_bag_quantity'),
    path('bag/move-to-wishlist/<str:cart_key>/', views.move_bag_to_wishlist, name='move_bag_to_wishlist'),
    path('place-order/', views.place_order, name='place_order'),
    
    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:pk>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/move-to-bag/<int:pk>/', views.move_wishlist_to_bag, name='move_wishlist_to_bag'),
    
    # Auth & Profile
    path('login/', views.user_login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile_view, name='profile'),
]