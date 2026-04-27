from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('questions/', views.questions, name="questions")
    path('stores/', views.stores, name="stores"),
    path('store/<uuid:store_id>/', views.store, name="store"),
    path('shop/', views.products, name="products"),
    path('product/<uuid:product_id>/', views.product, name="product"),
]
