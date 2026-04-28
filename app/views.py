from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.models import LoyaltyProgram, Cart, Order, OrderItem, Product, CartItem, Store, Coupon
from django.shortcuts import get_object_or_404

# Create your views here.


def index(request):
    # Render the home page displaying a list of all available stores
    stores = Store.objects.all()
    return render(request, "index.html", {"stores": stores} )

def questions(request):
    return render(request, "questions.html")

def techguide(request):
    return render(request, "tech-guide.html")

def guide(request):
    return render(request, "n-tech-guide.html")


def stores(request):
    # Render the stores directory page showing all stores and available coupons
    stores = Store.objects.all()
    coupons = Coupon.objects.all()
    return render(request, "stores.html", {"stores": stores, "coupons": coupons})

def store(request, store_id):
    # Render the detail view for a specific store and list its products
    store = get_object_or_404(Store, id=store_id)
    products = store.products.all()
    return render(request, "store_detail.html", {"store": store, "products": products})

def products(request):
    # Render the general shop page with all products grouped by category
    products = Product.objects.all()
    dairy_products = products.filter(type="Dairy & Eggs")
    fresh_products = products.filter(type="Fresh Produce")
    meat_products = products.filter(type="Meat & Seafood")
    pantry_products = products.filter(type="Pantry Staples")
    bakery_products = products.filter(type="Bakery")
    beverages_products = products.filter(type="Beverages")
    organic_products = products.filter(type="Organic")
    other_products = products.filter(type="Other")

    context = {"products": products,
        "dairy_products": dairy_products,
        "fresh_produce": fresh_products,
        "meat_products": meat_products,
        "pantry_products": pantry_products,
        "bakery_products": bakery_products,
        "beverages": beverages_products,
        "organic_products": organic_products,
        "other_products": other_products,
    }
    return render(request, "products.html", context)

def product(request, product_id):
    # Render the detail view for a specific product and suggest similar items
    product = get_object_or_404(Product, id=product_id)
    similar_products = Product.objects.filter(type=product.type).exclude(id=product.id)
    return render(request, "product_detail.html", {"product": product, "similar_products": similar_products} )