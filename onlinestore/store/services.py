from .models import Order, OrderItem, Cart, StockBalance


def create_order_from_cart(cart):
    """Создаёт заказ из корзины, уменьшает остатки, очищает корзину."""
    order = Order.objects.create(
        user=cart.user,
        total_price=cart.get_total_price()
    )
    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )
        stock = StockBalance.objects.filter(product=item.product).first()
        if stock:
            stock.quantity -= item.quantity
            stock.save()
    cart.items.all().delete()
    return order


def get_cart_contents(cart):
    """Возвращает содержимое корзины и общую сумму."""
    items = list(cart.items.all())
    total = cart.get_total_price()
    return items, total


def get_user_orders(user):
    """Возвращает все заказы пользователя."""
    return Order.objects.filter(user=user)


def ship_order(order):
    """Меняет статус заказа на 'Отправлен'."""
    order.status = 'shipped'
    order.save()
    return order


def check_stock(product, quantity):
    """Проверяет, достаточно ли товара на складе."""
    stock = StockBalance.objects.filter(product=product).first()
    if stock and quantity > stock.quantity:
        return False
    return True
