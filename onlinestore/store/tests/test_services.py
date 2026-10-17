import tempfile
from decimal import Decimal
from io import BytesIO

from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from PIL import Image

from store.models import Category, Product, StockBalance, Cart, Order, OrderItem
from store.services import create_order_from_cart

User = get_user_model()

TEST_MEDIA_ROOT = tempfile.mkdtemp()


def get_test_image():
    """Создаёт минимальное изображение для тестов."""
    img = Image.new('RGB', (1, 1), 'white')
    buf = BytesIO()
    img.save(buf, format='PNG')
    return SimpleUploadedFile('test.png', buf.getvalue(), content_type='image/png')


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class CreateOrderFromCartEdgeCasesTestCase(TestCase):
    """Тесты граничных случаев для create_order_from_cart."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.category = Category.objects.create(name='Электроника')

    def _create_product_and_stock(self, name, price, quantity):
        product = Product.objects.create(
            name=name, description='Тестовый товар',
            price=price, image=get_test_image(),
            category=self.category
        )
        StockBalance.objects.create(product=product, quantity=quantity)
        return product

    def test_insufficient_stock_raises_validation_error(self):
        """Если товара на складе меньше, чем в корзине — выбрасывается ValidationError."""
        product = self._create_product_and_stock('iPhone', '999.99', 2)
        cart = Cart.objects.create(user=self.user)
        cart.add_item(product, quantity=5)

        with self.assertRaises(ValidationError) as context:
            create_order_from_cart(cart)

        self.assertIn('Недостаточно товара', str(context.exception))

    def test_zero_stock_raises_validation_error(self):
        """Если остаток 0 — выбрасывается ValidationError."""
        product = self._create_product_and_stock('iPad', '599.99', 0)
        cart = Cart.objects.create(user=self.user)
        cart.add_item(product, quantity=1)

        with self.assertRaises(ValidationError):
            create_order_from_cart(cart)

    def test_no_stock_record_allows_order(self):
        """Если нет записи о остатке — заказ создаётся (нет блокировки)."""
        product = Product.objects.create(
            name='Book', description='Книга',
            price='499.99', image=get_test_image(),
            category=self.category
        )
        cart = Cart.objects.create(user=self.user)
        cart.add_item(product, quantity=1)

        order = create_order_from_cart(cart)
        self.assertIsNotNone(order)
        self.assertEqual(order.items.count(), 1)

    def test_multiple_items_in_order(self):
        """Заказ с несколькими разными товарами."""
        product1 = self._create_product_and_stock('iPhone', '999.99', 10)
        product2 = self._create_product_and_stock('iPad', '599.99', 10)
        product3 = self._create_product_and_stock('AirPods', '1499.99', 10)

        cart = Cart.objects.create(user=self.user)
        cart.add_item(product1, quantity=2)
        cart.add_item(product2, quantity=1)
        cart.add_item(product3, quantity=3)

        order = create_order_from_cart(cart)

        self.assertEqual(order.items.count(), 3)
        self.assertEqual(
            order.total_price,
            Decimal('999.99') * 2 + Decimal('599.99') * 1 + Decimal('1499.99') * 3
        )
        self.assertEqual(order.status, 'new')

    def test_stock_reduced_for_all_items(self):
        """Остатки уменьшаются для всех товаров в заказе."""
        product1 = self._create_product_and_stock('iPhone', '999.99', 10)
        product2 = self._create_product_and_stock('iPad', '599.99', 5)

        cart = Cart.objects.create(user=self.user)
        cart.add_item(product1, quantity=3)
        cart.add_item(product2, quantity=2)

        create_order_from_cart(cart)

        product1.refresh_from_db()
        product2.refresh_from_db()
        stock1 = StockBalance.objects.get(product=product1)
        stock2 = StockBalance.objects.get(product=product2)

        self.assertEqual(stock1.quantity, 7)
        self.assertEqual(stock2.quantity, 3)

    def test_exact_stock_allows_order(self):
        """Если остаток равен запросу — заказ создаётся."""
        product = self._create_product_and_stock('iPhone', '999.99', 5)
        cart = Cart.objects.create(user=self.user)
        cart.add_item(product, quantity=5)

        order = create_order_from_cart(cart)
        self.assertIsNotNone(order)

        stock = StockBalance.objects.get(product=product)
        self.assertEqual(stock.quantity, 0)

    def test_order_not_created_on_error_partial_data(self):
        """При ошибке на второй позиции — первая тоже не создаётся (атомарность)."""
        product1 = self._create_product_and_stock('iPhone', '999.99', 100)
        product2 = self._create_product_and_stock('iPad', '599.99', 0)

        cart = Cart.objects.create(user=self.user)
        cart.add_item(product1, quantity=1)
        cart.add_item(product2, quantity=1)

        with self.assertRaises(ValidationError):
            create_order_from_cart(cart)

        # Заказ не создан
        self.assertEqual(Order.objects.count(), 0)
        # Остаток product1 не изменён
        stock1 = StockBalance.objects.get(product=product1)
        self.assertEqual(stock1.quantity, 100)

    def test_empty_cart_creates_empty_order(self):
        """Пустая корзина создаёт заказ без позиций."""
        cart = Cart.objects.create(user=self.user)
        order = create_order_from_cart(cart)

        self.assertIsNotNone(order)
        self.assertEqual(order.items.count(), 0)
        self.assertEqual(order.total_price, 0)

    def test_cart_cleared_only_on_success(self):
        """Корзина очищается только при успешном создании заказа."""
        product = self._create_product_and_stock('iPhone', '999.99', 0)
        cart = Cart.objects.create(user=self.user)
        cart.add_item(product, quantity=1)

        with self.assertRaises(ValidationError):
            create_order_from_cart(cart)

        # Корзина не очищена
        self.assertEqual(cart.items.count(), 1)
