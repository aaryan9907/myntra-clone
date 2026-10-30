from django.db import models
from decimal import Decimal

class Category(models.Model):
    GENDER_CHOICES = [
        ('men', 'Men'),
        ('women', 'Women'),
        ('kids', 'Kids'),
        ('home', 'Home & Living'),
        ('beauty', 'Beauty'),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='men')

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return f"{self.name} ({self.get_gender_display()})"


class Product(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.PositiveIntegerField(default=0, help_text="e.g. 20 for 20% off")
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products')
    brand = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.PositiveIntegerField(default=0, help_text="e.g. 20 for 20% off")
    image = models.ImageField(upload_to='products/')
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.0)
    rating_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand} - {self.title}"

    @property
    def formatted_rating_count(self):
        count = self.rating_count
        if count >= 1_000_000:
            formatted = f"{count / 1_000_000:.1f}".rstrip('0').rstrip('.')
            return f"{formatted}M"
        elif count >= 1_000:
            formatted = f"{count / 1_000:.1f}".rstrip('0').rstrip('.')
            return f"{formatted}k"
        return str(count)

    @property
    def discounted_price(self):
        try:
            pct = int(self.discount_percentage or 0)
            if pct > 0:
                # Calculate discount: price * (100 - pct) / 100
                discount_factor = (Decimal(100) - Decimal(pct)) / Decimal(100)
                return int(round(self.price * discount_factor))
            return int(round(self.price))
        except Exception:
            return int(round(self.price)) if self.price else 0