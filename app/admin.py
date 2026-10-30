from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('brand', 'title', 'category', 'price', 'discount_percentage', 'rating')
    list_filter = ('category__gender', 'category', 'brand')
    search_fields = ('brand', 'title')