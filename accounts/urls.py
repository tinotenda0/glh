from django.urls import path
from . import views

urlpatterns = [
    # Main dashboard
    path('', views.dash, name="dash"),

    # Authentication views
    path('login/', views.login, name="login"),
    path('register/', views.register_customer, name="register_customer"),
    path('register_seller/', views.register_seller, name="register_seller"),
    path('logout/', views.logout, name="logout"),

    # Store management for sellers
    path('create_store/', views.create_store, name="create_store"),
    path('edit_store/<uuid:store_id>/', views.edit_store, name="edit_store"),
    path('delete_store/<uuid:store_id>/', views.delete_store, name="delete_store"),
    path('my_stores/', views.my_stores, name="my_stores"),
    path('store_dash/<uuid:store_id>/', views.store_dash, name="store_dash"),

    # Product management for sellers
    path('add_product/<uuid:store_id>/', views.add_product, name="add_product"),
    path('manage_products/<uuid:store_id>/', views.manage_products, name="manage_products"),
    path('edit_product/<uuid:product_id>/', views.edit_product, name="edit_product"),
    path('product_details/<uuid:product_id>/', views.product_details, name="product_details"),
    path('delete_product/<uuid:product_id>/', views.delete_product, name="delete_product"),

    # Cart functionality for customers
    path('add_to_cart/<uuid:product_id>/', views.add_to_cart, name="add_to_cart"),
    path('view_cart/', views.view_cart, name="view_cart"),
    path('remove_from_cart/<uuid:item_id>/', views.remove_from_cart, name="remove_from_cart"),
    path('update_cart_quantity/<uuid:item_id>/', views.update_cart_quantity, name="update_cart_quantity"),

    # Checkout process
    path('checkout/', views.checkout, name="checkout"),

    # Order history and management
    path('order_history/', views.order_history, name="order_history"),
    path('store_orders/<uuid:store_id>/', views.store_orders, name="store_orders"),
    path('update_order_status/<uuid:order_id>/', views.update_order_status, name="update_order_status"),

    # Loyalty program
    path('loyalty/', views.loyalty, name="loyalty"),

    # User profile
    path('profile/', views.my_profile, name="my_profile"),
    path('edit_profile/', views.edit_profile, name="edit_profile"),

    # Coupon management for sellers
    path('manage_coupons/<uuid:store_id>/', views.manage_coupons, name="manage_coupons"),
    path('add_coupon/<uuid:store_id>/', views.add_coupon, name="add_coupon"),
    path('edit_coupon/<uuid:coupon_id>/', views.edit_coupon, name="edit_coupon"),
    path('delete_coupon/<uuid:coupon_id>/', views.delete_coupon, name="delete_coupon"),

    # Coupon application for customers
    path('apply_coupon/', views.apply_coupon, name="apply_coupon"),
]
