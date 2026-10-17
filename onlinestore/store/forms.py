from django import forms
from .models import Product, Cart


class CartForm(forms.Form):
    """Форма для добавления товара в корзину."""

    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        label='Товар',
        help_text='Выберите товар из каталога'
    )
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        label='Количество',
        widget=forms.NumberInput(attrs={'min': '1', 'class': 'form-control'}),
        help_text='Укажите количество (минимум 1)'
    )


class OrderForm(forms.Form):
    """Форма для оформления заказа."""

    name = forms.CharField(
        max_length=255,
        label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваше имя'})
    )
    address = forms.CharField(
        max_length=500,
        label='Адрес доставки',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@mail.ru'})
    )
    cart = forms.ModelChoiceField(
        queryset=Cart.objects.all(),
        label='Корзина',
        widget=forms.HiddenInput()
    )
