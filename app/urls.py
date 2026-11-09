from django.urls import path
from . import views

urlpatterns = [
    path('', views.show, name='home'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    
    # Bag
    path('bag/', views.bag_view, name='bag'),
    path('bag/add/<int:pk>/', views.add_to_bag, name='add_to_bag'),
    path('bag/remove/<str:cart_key>/', views.remove_from_bag, name='remove_from_bag'),
    
    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:pk>/', views.toggle_wishlist, name='toggle_wishlist'),
    
    # Auth & Profile
    path('login/', views.user_login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile_view, name='profile'),
]