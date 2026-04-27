from django.db import models
from django.contrib.auth.models import User, AbstractUser
import uuid

store_categories = [
    ('Fruits & Vegetables', 'Fruits & Vegetables'),
    ('Dairy & Eggs', 'Dairy & Eggs'),
    ('Meat & Poultry', 'Meat & Poultry'),
    ('Grains & Cereals', 'Grains & Cereals'),
    ('Honey & Preserves', 'Honey & Preserves'),
    ('Bakery & Pastries', 'Bakery & Pastries'),
    ('Beverages', 'Beverages'),
    ('Organic & Specialty', 'Organic & Specialty'),
    ('Other', 'Other'),
]

product_types = [
    ('Fresh Produce', 'Fresh Produce'),
    ('Dairy & Eggs', 'Dairy & Eggs'),
    ('Meat & Seafood', 'Meat & Seafood'),
    ('Pantry Staples', 'Pantry Staples'),
    ('Bakery', 'Bakery'),
    ('Beverages', 'Beverages'),
    ('Snacks', 'Snacks'),
    ('Frozen Foods', 'Frozen Foods'),
    ('Household', 'Household'),
    ('Personal Care', 'Personal Care'),
    ('Organic', 'Organic'),
    ('Other', 'Other'),
]

# Represents a user, extending Django's AbstractUser with custom fields for roles.
class User(AbstractUser):
    is_customer = models.BooleanField(default=False)
    is_seller = models.BooleanField(default=False)
    image = models.ImageField(upload_to='avatars/', blank=True, null=True)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='accounts_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='accounts_user_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    
    def __str__(self):
        return self.username

# Represents a seller's store, containing details like name, owner, and category.
class Store(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='store_logos/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50, choices=store_categories, default='Other')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stores')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Represents an item available for sale within a store.
class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=50, choices=product_types, default='Other')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_out_of_stock = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# Manages a customer's loyalty points and membership tier.
class LoyaltyProgram(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.OneToOneField(User, on_delete=models.CASCADE, related_name='loyalty_account')
    points = models.PositiveIntegerField(default=0)
    tier = models.CharField(max_length=50, default='Bronze')
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer.username} - {self.points} points"

# Represents a discount coupon that can be applied to orders.
class Coupon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='coupons')
    discount_percentage = models.PositiveIntegerField()
    minimum_tier = models.CharField(max_length=50, default='Bronze')
    is_active = models.BooleanField(default=True)
    expiry_date = models.DateTimeField()

    def __str__(self):
        return f"{self.code} ({self.discount_percentage}% off)"

# Represents a customer's completed purchase from a single store.
class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.customer.username}"

# Represents a single line item within an order, linking a product with its quantity and price at purchase.
class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

# Represents a customer's shopping cart, which holds items before checkout.
class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.customer.username}"

# Represents a single item within a shopping cart, including its quantity.
class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in cart"
        