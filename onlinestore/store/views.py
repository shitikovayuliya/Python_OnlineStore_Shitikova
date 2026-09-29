from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import CartForm, OrderForm
from .models import Product, Category, Order, OrderItem, Cart, StockBalance
from django.contrib import messages

# Товары — уже сделано
def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})


# Категории
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'store/category_list.html', {'categories': categories})


def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    products = Product.objects.filter(category=category)
    return render(request, 'store/category_detail.html', {'category': category, 'products': products})


# Заказы
def order_list(request):
    orders = Order.objects.all()
    return render(request, 'store/order_list.html', {'orders': orders})


def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    items = order.items.all()
    return render(request, 'store/order_detail.html', {'order': order, 'items': items})


from django.contrib import messages


@login_required
def add_to_cart(request):
    if request.method == 'POST':
        form = CartForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']

            # Проверка остатка
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
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    total = cart.get_total_price()
    return render(request, 'store/cart.html', {'cart': cart, 'items': items, 'total': total})


@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Проверяем остатки для каждого товара
            for item in cart.items.all():
                stock = StockBalance.objects.filter(product=item.product).first()
                if stock and item.quantity > stock.quantity:
                    messages.error(request, f'Недостаточно товара «{item.product.name}» на складе (доступно {stock.quantity} шт.)')
                    return render(request, 'store/checkout.html', {'form': form, 'cart': cart})

            order = Order.objects.create(
                user=request.user,
                total_price=cart.get_total_price()
            )
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
                # Уменьшаем остаток на складе
                stock = StockBalance.objects.filter(product=item.product).first()
                if stock:
                    stock.quantity -= item.quantity
                    stock.save()

            cart.items.all().delete()
            messages.success(request, 'Заказ оформлен!')
            return redirect('order_detail', pk=order.pk)
    else:
        form = OrderForm()
    return render(request, 'store/checkout.html', {'form': form, 'cart': cart})
