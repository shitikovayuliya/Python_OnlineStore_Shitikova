from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Category(models.Model):
    """Категория товаров (например: Электроника, Одежда, Книги)."""

    name = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание', help_text='Необязательное описание категории')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Product(models.Model):
    """Товар: название, описание, цена, изображение, категория."""

    name = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Цена',
        help_text='Цена в рублях, максимум 999 999.99'
    )
    image = models.ImageField(upload_to='products/', verbose_name='Изображение')
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, verbose_name='Категория',
        help_text='Защита: нельзя удалить категорию, если есть товары'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class Order(models.Model):
    """Заказ пользователя: список товаров, статус, сумма."""

    STATUS_CHOICES = [
        ('new', 'Новый'),          # Заказ только создан
        ('processing', 'В обработке'),  # Обрабатывается
        ('shipped', 'Отправлен'),   # Отправлен покупателю
        ('delivered', 'Доставлен'), # Доставлен
        ('cancelled', 'Отменён'),   # Отменён
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name='Итоговая сумма'
    )
    is_paid = models.BooleanField(default=False, verbose_name='Оплачен')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Статус'
    )

    def __str__(self):
        return f'Заказ №{self.id} — {self.user}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class OrderItem(models.Model):
    """Позиция в заказе: товар, количество, цена на момент покупки."""

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ'
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Товар')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Цена',
        help_text='Цена товара на момент оформления заказа'
    )

    def __str__(self):
        return f'{self.product.name} × {self.quantity}'

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

class Cart(models.Model):
    """Корзина пользователя: содержит товары перед оформлением заказа."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return f'Корзина — {self.user}'

    def add_item(self, product, quantity=1):
        """
        Добавить товар в корзину.
        Если товар уже есть — увеличивает количество.
        """
        item, created = CartItem.objects.get_or_create(
            cart=self, product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            item.quantity += quantity
            item.save()

    def get_total_price(self):
        """Вычисляет общую стоимость всех товаров в корзине."""
        return sum(item.product.price * item.quantity for item in self.items.all())

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'


class CartItem(models.Model):
    """Позиция в корзине: товар и количество."""

    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='items', verbose_name='Корзина'
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Товар')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')

    def __str__(self):
        return f'{self.product.name} × {self.quantity}'

    class Meta:
        verbose_name = 'Позиция корзины'
        verbose_name_plural = 'Позиции корзины'


class StockBalance(models.Model):
    """Остаток товара на складе: используется для проверки перед оформлением заказа."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveIntegerField(default=0, verbose_name='Остаток')

    def __str__(self):
        return f'{self.product.name} — {self.quantity} шт.'

    class Meta:
        verbose_name = 'Остаток товара'
        verbose_name_plural = 'Остатки товаров'


class Customer(models.Model):
    """Профиль клиента: дополнительные данные о покупателе."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    full_name = models.CharField(max_length=255, verbose_name='ФИО')
    address = models.TextField(verbose_name='Адрес доставки')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
