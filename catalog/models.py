from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    icon_class = models.CharField(max_length=50, default='fas fa-book', help_text='Font Awesome 6 icon class')
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class Product(models.Model):
    STOCK_STATUS_CHOICES = [
        ('IN_STOCK', 'In Stock'),
        ('AVAILABLE_ON_ORDER', 'Available on Order'),
        ('BACKORDER_ALLOWED', 'Backorder Allowed'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    sku = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    retail_price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Price per single piece in GH₵')
    wholesale_price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Wholesale carton/bulk price in GH₵')
    wholesale_box_size = models.CharField(max_length=100, default='Box of 120', help_text='e.g. Box of 120, Carton of 48, Pack of 50')
    stock_status = models.CharField(max_length=25, choices=STOCK_STATUS_CHOICES, default='IN_STOCK')
    stock_quantity = models.PositiveIntegerField(default=100, help_text='Internal warehouse quantity. Strictly concealed from customers per company policy.')
    icon_class = models.CharField(max_length=50, default='fas fa-book', help_text='Font Awesome icon class')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_customizable = models.BooleanField(default=False, help_text='Can be ordered with custom school crests & rulings')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def stock_badge_class(self):
        if self.stock_status == 'IN_STOCK':
            return 'badge-stock-in'
        elif self.stock_status == 'AVAILABLE_ON_ORDER':
            return 'badge-stock-order'
        return 'badge-stock-backorder'
