from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Order, OrderItem, Cart, StockBalance


def create_order_from_cart(cart):
    """
    Атомарное создание заказа из корзины.

    Гарантии:
    - transaction.atomic(): если ошибка на любом шаге — всё откатывается
    - select_for_update(): блокировка строк остатков для предотвращения гонок
    - Проверка остатков перед созданием OrderItem

    Args:
        cart: Корзина пользователя с товарами

    Returns:
        Order: Созданный заказ

    Raises:
        ValidationError: Если товара недостаточно на складе
    """
    with transaction.atomic():
        # Создаём заказ с итоговой суммой
        order = Order.objects.create(
            user=cart.user,            total_price=cart.get_total_price()
        )

        # Обрабатываем каждую позицию корзины
        for item in cart.items.all():
            # Блокируем строку остатка для чтения/изменения
            stock = StockBalance.objects.select_for_update().filter(product=item.product).first()

            # Проверяем, достаточно ли товара на складе
            if stock and item.quantity > stock.quantity:
                raise ValidationError(
                    f'Недостаточно товара «{item.product.name}» на складе '
                    f'(доступно {stock.quantity} шт.)'
                )

            # Создаём позицию заказа с ценой на момент покупки
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

            # Уменьшаем остаток на складе
            if stock:
                stock.quantity -= item.quantity
                stock.save()

        # Очищаем корзину после успешного оформления
        cart.items.all().delete()

    return order


def get_cart_contents(cart):
    """
    Получает содержимое корзины.

    Returns:
        tuple: (список позиций, общая сумма)
    """
    items = list(cart.items.all())
    total = cart.get_total_price()
    return items, total


def get_user_orders(user):
    """
    Получает все заказы пользователя, отсортированные по дате (новые первые).

    Args:
        user: Экземпляр пользователя

    Returns:
        QuerySet: queryset заказов
    """
    return Order.objects.filter(user=user).order_by('-created_at')


def ship_order(order):
    """
    Меняет статус заказа на 'Отправлен'.

    Args:
        order: Экземпляр заказа

    Returns:
        Order: обновлённый заказ
    """
    order.status = 'shipped'
    order.save()
    return order


def check_stock(product, quantity):
    """
    Проверяет, достаточно ли товара на складе.

    Args:
        product: Экземпляр товара
        quantity: Запрашиваемое количество

    Returns:
        bool: True если товара достаточно или нет записи о остатке
    """
    stock = StockBalance.objects.filter(product=product).first()
    if stock and quantity > stock.quantity:
        return False
    return True
