import uuid
import random
from django.contrib.auth import get_user_model
from accounts.models import Store, Product

# This script creates a total of 10 stores and 50 products for each store.
# To excecute the script, run: python manage.py shell
# Then copy and paste the entire script into the Django shell, press enter, and wait for the script to finish.
# Press Ctrl+Z and then press enter to exit the python shell.

# Get the User model
User = get_user_model()

# 1. Properly unpack the tuple and ensure the user is a seller
# get_or_create returns (user_instance, created_bool)
user, created = User.objects.get_or_create(
    username='admin', 
    defaults={
        'is_staff': True, 
        'is_superuser': True,
        'is_seller': True,
        'is_customer': False
    }
)

# If the user already existed but wasn't a seller, update them
if not created and not user.is_seller:
    user.is_seller = True
    user.save()

stores_to_create = [
        ('Green Earth Veggies', 'Fruits & Vegetables', 'Fresh local produce'),
        ('The Dairy Barn', 'Dairy & Eggs', 'Organic milk and cheese'),
        ('Prime Cuts Butchery', 'Meat & Poultry', 'Premium meats and poultry'),
        ('Golden Grain Mill', 'Grains & Cereals', 'Stone-ground grains and cereals'),
        ('Sweet Nectar Shop', 'Honey & Preserves', 'Local honey and artisan preserves'),
        ('Rise & Shine Bakery', 'Bakery & Pastries', 'Freshly baked pastries'),
        ('Crystal Springs', 'Beverages', 'Artisanal beverages and water'),
        ('Specially Yours', 'Organic & Specialty', 'Gourmet and organic finds'),
        ('The Pantry Corner', 'Other', 'Essential cooking staples and spices'),
        ('Sunrise Orchard', 'Fruits & Vegetables', 'Apples and orchard fruits'),
    ]

product_pool = {
    'Fruits & Vegetables': [('Apples', 'Fresh Produce'), ('Kale', 'Fresh Produce'), ('Carrots', 'Fresh Produce'), ('Pears', 'Fresh Produce'), ('Potatoes', 'Fresh Produce')],
    'Dairy & Eggs': [('Whole Milk', 'Dairy & Eggs'), ('Cheddar', 'Dairy & Eggs'), ('Butter', 'Dairy & Eggs'), ('Eggs', 'Dairy & Eggs'), ('Yogurt', 'Dairy & Eggs')],
    'Meat & Poultry': [('Chicken', 'Meat & Seafood'), ('Beef', 'Meat & Seafood'), ('Pork', 'Meat & Seafood'), ('Salmon', 'Meat & Seafood'), ('Mackerel', 'Meat & Seafood')],
    'Grains & Cereals': [('Oats', 'Pantry Staples'), ('Rice', 'Pantry Staples'), ('Quinoa', 'Pantry Staples'), ('Barley', 'Pantry Staples'), ('Wheat', 'Pantry Staples')],
    'Honey & Preserves': [('Raw Honey', 'Pantry Staples'), ('Jam', 'Pantry Staples'), ('Marmalade', 'Pantry Staples'), ('Sweet Potato', 'Pantry Staples'), ('Honeycomb', 'Pantry Staples')],
    'Bakery & Pastries': [('Sourdough', 'Bakery'), ('Croissant', 'Bakery'), ('Muffin', 'Bakery'), ('Bread', 'Bakery'), ('Pancakes', 'Bakery')],
    'Beverages': [('Coffee', 'Beverages'), ('Tea', 'Beverages'), ('Orange Juice', 'Beverages'), ('Kiwi & Blackberry Juice', 'Beverages'), ('Apple Cider', 'Beverages')],
    'Organic & Specialty': [('Kombucha', 'Organic'), ('Tofu', 'Organic'), ('Tempeh', 'Organic'), ('Corn', 'Organic'), ('Cabbage', 'Organic')],
    'Other': [('Olive Oil', 'Pantry Staples'), ('Sea Salt', 'Pantry Staples'), ('Black Pepper', 'Pantry Staples'), ('Pasta', 'Pantry Staples'), ('Lentils', 'Pantry Staples')],
}

print(f"Seeding stores for user: {user.username}...")

# Create stores and products
# Note: This implementation does not handle duplicates and products can be duplicated across stores.
for s_name, s_cat, s_desc in stores_to_create:
    store = Store.objects.create(
        name=s_name,
        category=s_cat,
        description=s_desc,
        owner=user
    )
    
    # Get products for this category, or default to 'Other' list
    items = product_pool.get(s_cat, product_pool['Other'])
    
    # Generate 5 products (cycling through the pool if pool is < 5)
    for i in range(5):
        p_name, p_type = items[i % len(items)]
        Product.objects.create(
            store=store,
            name=f"{p_name}",
            description=f"High quality {p_name.lower()} from {s_name}.",
            type=p_type,
            price=round(random.uniform(5.0, 50.0), 2),
            stock_quantity=random.randint(10, 100),
            is_out_of_stock=False
        )