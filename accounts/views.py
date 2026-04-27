from django.shortcuts import render
from accounts.models import LoyaltyProgram, Cart, Order, OrderItem, Product, CartItem, User
from decimal import Decimal
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import user_passes_test, login_required
from accounts.forms import UserRegistrationForm, CreateStoreForm, ProductForm, EditProfileForm
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect

def group_required(*group_names):
    # Decorator to check if a user belongs to specific groups or is a superuser
    def in_groups(u):
        # Inner function to check user group membership
        if u.is_authenticated:
            if bool(u.groups.filter(name__in=group_names)) or u.is_superuser:
                return True
        return False
    return user_passes_test(in_groups)

def is_logged_out(user):
    # Decorator to restrict access to views for logged-out users only
    return user_passes_test(lambda u: not u.is_authenticated, login_url='dash')(user)
    
    

def dash(request):
    # Render the main dashboard view
    return render(request, "dash.html")

@is_logged_out
def login(request):
    # Handle user login, authenticate credentials, and redirect to the dashboard
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            from django.contrib.auth import login as auth_login
            user = form.get_user()
            auth_login(request, user)
            return render(request, "dash.html", {"message": f"Welcome back, {user.username}!"})
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})
    
@is_logged_out
def register_customer(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST, request.FILES or None)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_customer = True
            user.save()
            group = Group.objects.get(name='Customer')
            user.groups.add(group)
            user.save()
            LoyaltyProgram.objects.create(customer=user)
            Cart.objects.create(customer=user)
            from django.contrib.auth import login as auth_login
            auth_login(request, user)
            return render(request, "dash.html", {"message": "Customer account created successfully!"})
            
            
    else:
        form = UserRegistrationForm()
    return render(request, "register_customer.html", {"form": form, "role": "Customer"})

@group_required('Customer')
@login_required
def register_seller(request):
    # Handle seller registration for existing logged-in customers, updating their roles
    if request.method == "POST":
        user = request.user
        if not user.is_seller:
            user.is_seller = True
            user.is_customer = False
            group = Group.objects.get(name='Seller')
            customer = Group.objects.get(name='Customer')
            user.groups.remove(customer)
            user.groups.add(group)
            user.save()
            return render(request, "dash.html", {"message": "You are now registered as a Seller!"})
        else:
            return render(request, "dash.html", {"message": "You are already a Seller."})
    return render(request, "register_seller.html")

@login_required
# Edit user details
def edit_profile(request):
    # Handle updating the user's profile information
    from accounts.forms import UserRegistrationForm
    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES or None, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('my_profile')
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, "edit_profile.html", {"form": form})


def logout(request):
    # Handle user logout and redirect to the index page
    from django.contrib.auth import logout as auth_logout
    auth_logout(request)
    return render(request, "index.html")

@group_required('Seller')
def create_store(request):
    # Handle the creation of a new store by a seller
    form = CreateStoreForm(request.POST, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        store = form.save(commit=False)
        store.owner = request.user
        store.save()
        return render(request, "dash.html", {"message": "Store created successfully!"})
    return render(request, "create_store.html", {"form": form})

@group_required('Seller')
def edit_store(request, store_id):
    # Handle updating an existing store's details
    from accounts.models import Store
    from django.shortcuts import get_object_or_404, redirect
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    if request.method == "POST":
        form = CreateStoreForm(request.POST, request.FILES or None, instance=store)
        if form.is_valid():
            form.save()
            return redirect('my_stores')
    else:
        form = CreateStoreForm(instance=store)
    return render(request, "edit_store.html", {"form": form, "store": store})

@group_required('Seller')
def delete_store(request, store_id):
    # Handle the deletion of an existing store
    from accounts.models import Store
    from django.shortcuts import get_object_or_404
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    if request.method == "POST":
        store.delete()
        return render(request, "dash.html", {"message": "Store deleted successfully!"})
    return render(request, "confirm_delete_store.html", {"store": store})

@group_required('Seller')
def my_stores(request):
    # Render a list of all stores owned by the current seller
    from accounts.models import Store
    stores = Store.objects.filter(owner=request.user)
    return render(request, "my_stores.html", {"stores": stores})

def store_dash(request, store_id):
    # Render the specific dashboard for a store, showing products and orders
    from accounts.models import Store
    from django.shortcuts import get_object_or_404
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    products = store.products.all()
    orders = store.orders.all()
    return render(request, "store_dash.html", {"store": store, "products": products, "orders": orders})
    

@group_required('Seller')
def add_product(request, store_id):
    # Handle adding a new product to a specific store
    form = ProductForm(request.POST, request.FILES or None)
    from accounts.models import Store
    from django.shortcuts import get_object_or_404
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    if request.method == "POST" and form.is_valid():
        product = form.save(commit=False)
        product.store = store
        product.save()
        return render(request, "dash.html", {"message": "Product added successfully!"})
    return render(request, "add_product.html", {"form": form, "store": store})

@group_required('Seller')
def manage_products(request, store_id):
    # Render the management view for a store's products and associated order items
    from accounts.models import Store, OrderItem
    from django.shortcuts import get_object_or_404
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    products = store.products.all()
    # Get all order items associated with products in this store
    order_items = OrderItem.objects.filter(product__store=store).select_related('order', 'product')
    
    return render(request, "manage_product.html", {
        "store": store, 
        "products": products,
        "order_items": order_items
    })

@group_required('Seller')
def edit_product(request, product_id):
    # Handle updating an existing product's details and adjust out-of-stock status
    from accounts.models import Product
    from django.shortcuts import get_object_or_404
    product = get_object_or_404(Product, id=product_id, store__owner=request.user)
    store = product.store
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES or None, instance=product)
        if form.is_valid():
            form.save()
            # Update out of stock status if stock = more than 1
            if product.stock_quantity >= 1:
                product.is_out_of_stock = False
                product.save()
            else:
                product.is_out_of_stock = True
                product.save()
            return redirect('manage_products', store_id=store.id)
    else:
        form = ProductForm(instance=product)
    return render(request, "edit_product.html", {"form": form, "product": product, "store": store})

@group_required('Seller')
def delete_product(request, product_id):
    # Handle the deletion of an existing product from a store
    from accounts.models import Product
    from django.shortcuts import get_object_or_404
    product = get_object_or_404(Product, id=product_id, store__owner=request.user)
    store = product.store
    if request.method == "POST":
        product.delete()
        return redirect('store_dash', store_id=store.id)
        
        
    return render(request, "confirm_delete_product.html", {"product": product, "store": store})

@group_required('Seller')
def product_details(request, product_id):
    # Render the details of a specific product and its associated order items
    from accounts.models import Product, OrderItem
    from django.shortcuts import get_object_or_404
    product = get_object_or_404(Product, id=product_id, store__owner=request.user)
    order_items = OrderItem.objects.filter(product=product).select_related('order')
    
    return render(request, "product_details.html", {
        "product": product,
        "order_items": order_items
    })
    

@login_required
def add_to_cart(request, product_id):
    # Add a product to the user's cart or increment its quantity if it already exists
    from accounts.models import Product, Cart, CartItem
    from django.shortcuts import get_object_or_404
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(customer=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        
    return redirect('view_cart')

@login_required
def view_cart(request):
    # Render the user's cart, calculating totals and applying coupon discounts if any
    from accounts.models import Cart
    cart, created = Cart.objects.get_or_create(customer=request.user)
    cart_items = cart.items.all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    final_total = total_price - (total_price * Decimal(request.session.get('applied_coupon', {}).get('discount_percentage', 0)) / 100)
    final_total = round(final_total, 2)
    
    return render(request, "view_cart.html", {
        "cart": cart,
        "cart_items": cart_items,
        "total_price": total_price,
        "final_total": final_total,
    })

@login_required
def checkout(request):
    # Handle the checkout process, applying discounts, deducting points, creating orders, and updating stock
    from accounts.models import Cart, Order, OrderItem, LoyaltyProgram
    from django.shortcuts import get_object_or_404
    
    cart = get_object_or_404(Cart, customer=request.user)
    cart_items = cart.items.all()
    
    if not cart_items:
        return redirect('view_cart')

    # Calculate total
    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    loyalty_account, _ = LoyaltyProgram.objects.get_or_create(customer=request.user)

    # Handle Coupon Discount from session
    coupon_data = request.session.get('applied_coupon')
    coupon_discount_decimal = Decimal(0)
    if coupon_data:
        coupon_discount_decimal = total_amount * (Decimal(coupon_data['discount_percentage']) / Decimal(100))

    # Initial calculation for display
    final_total = total_amount - coupon_discount_decimal
    final_total = round(final_total, 2)
    total_saved = coupon_discount_decimal
    total_saved = round(total_saved, 2)


    if request.method == "POST":
        use_points = request.POST.get('use_points') == 'on'
        points_discount = Decimal(0)
        
        # Handle Loyalty Points Discount
        if use_points and loyalty_account.points > 0:
            # 10 points = $1 discount
            points_discount_value = Decimal(loyalty_account.points) / Decimal(10)
            points_discount = min(final_total, points_discount_value)
            loyalty_account.points -= int(points_discount * 10)
            loyalty_account.save()
        
        final_total = final_total - points_discount
        points = int(points_discount * 10)
        final_total = round(final_total, 2)
        total_saved = round(total_saved + points_discount, 2)

        # Group items by store to create separate orders
        stores = set(item.product.store for item in cart_items)
        
        for store in stores:
            store_items = cart_items.filter(product__store=store)
            store_subtotal = sum(item.product.price * item.quantity for item in store_items)
            # Create the Order
            order = Order.objects.create(
                customer=request.user,
                store=store,
                total_amount=store_subtotal,
                status='Paid'
            )
            
            # Create OrderItems and update stock
            for item in store_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price_at_purchase=item.product.price
                )
                # Update stock
                item.product.stock_quantity -= item.quantity
                if item.product.stock_quantity <= 0:
                    item.product.is_out_of_stock = True
                item.product.save()

        # Clear the cart after successful checkout
        cart_items.delete()
        
        # Add points for the purchase (1 point per $1 spent)
        loyalty_account.points += int(total_amount)
        loyalty_account.save()

        # Clear coupon from session after use
        if 'applied_coupon' in request.session:
            del request.session['applied_coupon']

        return render(request, "dash.html", {"message": "Order placed successfully!"})

    return render(request, "checkout.html", {
        "cart": cart,
        "cart_items": cart_items,
        "total_amount": total_amount,
        "loyalty_account": loyalty_account,
        "final_total": final_total,
        "total_saved": total_saved,
    })
    

@login_required
def update_cart_quantity(request, item_id):
    # Increase or decrease the quantity of a specific item in the cart
    from accounts.models import CartItem
    from django.shortcuts import get_object_or_404
    
    # Accommodate the template passing either the CartItem ID or the Product ID
    cart_item = CartItem.objects.filter(id=item_id, cart__customer=request.user).first()
    if not cart_item:
        cart_item = get_object_or_404(CartItem, product_id=item_id, cart__customer=request.user)
        
    if request.method == "POST":
        action = request.POST.get('action')
        if action == "increase":
            cart_item.quantity += 1
            cart_item.save()
        elif action == "decrease":
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
        
    return redirect('view_cart')

@login_required
def remove_from_cart(request, item_id):
    # Remove a specific item entirely from the user's cart
    from accounts.models import CartItem
    from django.shortcuts import get_object_or_404

    # Accommodate the template passing either the CartItem ID or the Product ID
    cart_item = CartItem.objects.filter(id=item_id, cart__customer=request.user).first()
    if not cart_item:
        cart_item = get_object_or_404(CartItem, product_id=item_id, cart__customer=request.user)

    cart_item.delete()
    return redirect('view_cart')
    
    
@login_required
def order_history(request):
    # Render a list of past orders made by the customer
    from accounts.models import Order
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, "order_history.html", {"orders": orders})

@group_required('Seller')
def store_orders(request, store_id):
    # Render a list of orders placed at a specific store for the seller to view
    from accounts.models import Store, Order
    from django.shortcuts import get_object_or_404
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    orders = Order.objects.filter(store=store).order_by('-created_at')
    return render(request, "store_orders.html", {"store": store, "orders": orders})

@group_required('Seller')
def update_order_status(request, order_id):
    # Update the status of a specific order (e.g., Pending, Paid, Shipped)
    from accounts.models import Order
    from django.shortcuts import get_object_or_404
    order = get_object_or_404(Order, id=order_id, store__owner=request.user)
    if request.method == "POST":
        new_status = request.POST.get('status')
        if new_status:
            order.status = new_status
            order.save()
            return redirect('store_orders', store_id=order.store.id)
    return render(request, "update_order_status.html", {"order": order})

# Loyalty Program Logic
@login_required
def loyalty (request):
    # Render the user's loyalty account details and update their tier based on current points
    from accounts.models import LoyaltyProgram
    loyalty_account, created = LoyaltyProgram.objects.get_or_create(customer=request.user)
    
    # Simple logic to update tiers based on points
    if loyalty_account.points >= 1000:
        loyalty_account.tier = 'Gold'
    elif loyalty_account.points >= 500:
        loyalty_account.tier = 'Silver'
    else:
        loyalty_account.tier = 'Bronze'
    loyalty_account.save()

    return render(request, "loyalty.html", {"loyalty_account": loyalty_account})

@login_required
def my_profile(request):
    # Render the user's profile, summarising their orders, products, and total spent
    from accounts.models import User, Order, Product
    user = request.user
    my_orders = Order.objects.filter(customer=user)
    products = Product.objects.filter(store__owner=user)
    orders = Order.objects.filter(store__owner=user)
    total_spent = sum(order.total_amount for order in my_orders)


    context = {
        "user": user,
        "my_orders": my_orders,
        "products": products,
        "orders": orders,
        "total_spent": total_spent,
    }

    return render(request, "profile.html", context)

@group_required('Seller')
def add_coupon(request, store_id):
    # Handle creating a new coupon for a specific store
    from accounts.models import Coupon, Store
    from accounts.forms import CouponForm
    from django.shortcuts import get_object_or_404
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    if request.method == "POST":
        form = CouponForm(request.POST)
        if form.is_valid():
            coupon = form.save(commit=False)
            coupon.store = store
            form.save()
            return redirect('manage_coupons', store_id=store.id)
    else:
        form = CouponForm()
    return render(request, "add_coupon.html", {"form": form, "store": store})

@group_required('Seller')
def edit_coupon(request, coupon_id):
    # Handle updating an existing coupon's details
    from accounts.models import Coupon, Store
    from accounts.forms import CouponForm
    from django.shortcuts import get_object_or_404, redirect
    
    coupon = get_object_or_404(Coupon, id=coupon_id)
    store = coupon.store
    if request.method == "POST":
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            return redirect('manage_coupons', store_id=store.id)
    else:
        form = CouponForm(instance=coupon)
    return render(request, "edit_coupon.html", {"form": form, "coupon": coupon, "store": store})
    

@group_required('Seller')
def delete_coupon(request, coupon_id):
    # Handle deleting a specific coupon
    from accounts.models import Coupon
    from django.shortcuts import get_object_or_404, redirect
    coupon = get_object_or_404(Coupon, id=coupon_id, store__owner=request.user)
    store = coupon.store
    if request.method == "POST":
        coupon.delete()
        return redirect('manage_coupons', store_id=store.id)
    return render(request, "confirm_delete_coupon.html", {"coupon": coupon, "store": store})
    
    
@group_required('Seller')
def manage_coupons(request, store_id):
    # Render a list of all coupons and specific ones for the seller's store
    from accounts.models import Coupon, Store
    from django.shortcuts import get_object_or_404
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    coupons = Coupon.objects.all()
    my_coupons = Coupon.objects.filter(store=store)
    return render(request, "manage_coupons.html", {"coupons": coupons, "store": store, "my_coupons": my_coupons})

@login_required
def apply_coupon(request):
    # Apply a coupon code to the user's session if valid and if the user meets the tier requirement
    from accounts.models import Coupon, LoyaltyProgram
    from django.utils import timezone
    from django.contrib import messages

    if request.method == "POST":
        code = request.POST.get('coupon_code')
        try:
            coupon = Coupon.objects.get(code=code, is_active=True, expiry_date__gt=timezone.now())
            loyalty_account = LoyaltyProgram.objects.get(customer=request.user)
            
            # Check if user meets the tier requirement
            tiers = ['Bronze', 'Silver', 'Gold']
            user_tier_index = tiers.index(loyalty_account.tier)
            required_tier_index = tiers.index(coupon.minimum_tier)
            
            if user_tier_index >= required_tier_index:
                request.session['applied_coupon'] = {
                    'code': coupon.code,
                    'discount_percentage': coupon.discount_percentage
                }
                messages.success(request, f"Coupon '{code}' applied successfully!")
            else:
                messages.error(request, f"This coupon requires {coupon.minimum_tier} tier.")
                
        except Coupon.DoesNotExist:
            messages.error(request, "Invalid or expired coupon code.")
            
    return redirect('view_cart')
    