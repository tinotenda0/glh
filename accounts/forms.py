from django import forms
from accounts.models import User, Store, Product, Coupon
from django.contrib.auth.forms import UserCreationForm
        
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length = 20)
    last_name = forms.CharField(max_length = 20)
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'image', 'password1', 'password2']

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'image']

class CreateStoreForm(forms.ModelForm):
    class Meta:
        model = Store
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        
        fields = ['name', 'description', 'image', 'category']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'type', 'image', 'stock_quantity']

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount_percentage', 'minimum_tier', 'is_active', 'expiry_date']
        widgets = {
            'expiry_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        
        