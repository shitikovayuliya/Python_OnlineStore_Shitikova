from django import forms
from .models import Product, Cart


class CartForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), label='Товар')
    quantity = forms.IntegerField(min_value=1, initial=1, label='Количество')


class OrderForm(forms.Form):
    name = forms.CharField(label='Имя')
    address = forms.CharField(label='Адрес доставки')
    email = forms.EmailField(label='Email')
    cart = forms.ModelChoiceField(queryset=Cart.objects.all(), label='Корзина')
