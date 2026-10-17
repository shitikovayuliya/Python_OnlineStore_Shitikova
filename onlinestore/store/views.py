from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from .forms import CartForm, OrderForm
from .models import Product, Category, Order, OrderItem, Cart, StockBalance
from .services import create_order_from_cart
from django.contrib import messages


# =============================================================================
# Каталог товаров
# =============================================================================

def product_list(request):
    """Страница со списком всех товаров."""
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})


def product_detail(request, pk):
    """Страница детального просмотра одного товара."""
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})


# =============================================================================
# Категории
# =============================================================================

def category_list(request):
    """Страница со списком всех категорий."""
    categories = Category.objects.all()
    return render(request, 'store/category_list.html', {'categories': categories})


def category_detail(request, pk):
    """Страница категории со списком товаров этой категории."""
    category = get_object_or_404(Category, pk=pk)
    products = Product.objects.filter(category=category)
    return render(request, 'store/category_detail.html', {'category': category, 'products': products})


# =============================================================================
# Заказы (требуют авторизации)
# =============================================================================

@login_required
def order_list(request):
    """
    Список заказов текущего пользователя.
    Только авторизованные пользователи видят свои заказы.
    """
    orders = Order.objects.filter(user=request.user)
    return render(request, 'store/order_list.html', {'orders': orders})


@login_required
def order_detail(request, pk):
    """
    Детальный просмотр заказа.
    Проверка: пользователь видит только свои заказы.
    """
    order = get_object_or_404(Order, pk=pk)
    if order.user != request.user:
        messages.error(request, 'У вас нет доступа к этому заказу')
        return redirect('order_list')
    items = order.items.all()
    return render(request, 'store/order_detail.html', {'order': order, 'items': items})


# =============================================================================
# Корзина (требуют авторизации)
# =============================================================================

@login_required
def add_to_cart(request):
    """
    Добавить товар в корзину.
    Проверяет доступный остаток на складе перед добавлением.
    """
    if request.method == 'POST':
        form = CartForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']

            # Проверка остатка на складе
            stock = StockBalance.objects.filter(product=product).first()
            if stock and quantity > stock.quantity:
                messages.error(request, f'На складе только {stock.quantity} шт. товара «{product.name}»')
                return render(request, 'store/add_to_cart.html', {'form': form})

            cart, created = Cart.objects.get_or_create(user=request.user)
            cart.add_item(product, quantity)
            messages.success(request, 'Товар добавлен в корзину')
            return redirect('cart')
    else:
        form = CartForm()
    return render(request, 'store/add_to_cart.html', {'form': form})


@login_required
def cart_view(request):
    """Страница корзины: показывает выбранные товары и итоговую сумму."""
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    total = cart.get_total_price()
    return render(request, 'store/cart.html', {'cart': cart, 'items': items, 'total': total})


@login_required
def checkout(request):
    """
    Оформление заказа:
    1. Проверяет форму
    2. Вызывает сервис create_order_from_cart (атомарная операция)
    3. Очищает корзину, уменьшает остатки
    """
    cart, created = Cart.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            try:
                order = create_order_from_cart(cart)
                messages.success(request, 'Заказ оформлен!')
                return redirect('order_detail', pk=order.pk)
            except ValidationError as e:
                messages.error(request, e.message)
    else:
        form = OrderForm()
    return render(request, 'store/checkout.html', {'form': form, 'cart': cart})
