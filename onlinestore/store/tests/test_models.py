import tempfile
from decimal import Decimal
from io import BytesIO

from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from PIL import Image

from store.models import (
    Category, Product, Order, OrderItem, Cart, CartItem,
    StockBalance, Customer
)

User = get_user_model()

TEST_MEDIA_ROOT = tempfile.mkdtemp()


def get_test_image():
    """Создаёт минимальное изображение для тестов."""
    img = Image.new('RGB', (1, 1), 'white')
    buf = BytesIO()
    img.save(buf, format='PNG')
    return SimpleUploadedFile('test.png', buf.getvalue(), content_type='image/png')


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class CategoryTestCase(TestCase):
    def test_category_creation(self):
        category = Category.objects.create(name='Электроника', description='Гаджеты')
        self.assertEqual(category.name, 'Электроника')
        self.assertEqual(category.description, 'Гаджеты')
        self.assertEqual(str(category), 'Электроника')

    def test_category_blank_description(self):
        category = Category.objects.create(name='Книги')
        self.assertEqual(category.description, '')


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ProductTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Электроника')

    def test_product_creation(self):
        product = Product.objects.create(
            name='iPhone', description='Смартфон',
            price='999.99', image=get_test_image(),
            category=self.category
        )
        product.refresh_from_db()
        self.assertEqual(product.name, 'iPhone')
        self.assertEqual(product.price, Decimal('999.99'))
        self.assertEqual(str(product), 'iPhone')

    def test_product_category_relation(self):
        product = Product.objects.create(
            name='iPhone', description='Смартфон',
            price='999.99', image=get_test_image(),
            category=self.category
        )
        self.assertEqual(product.category, self.category)


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class CartTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.category = Category.objects.create(name='Электроника')
        self.product = Product.objects.create(
            name='iPhone', description='Смартфон',
            price='999.99', image=get_test_image(),
            category=self.category
        )
        self.cart = Cart.objects.create(user=self.user)

    def test_cart_creation(self):
        self.assertEqual(self.cart.user, self.user)
        self.assertEqual(str(self.cart), f'Корзина — {self.user}')

    def test_add_item_new(self):
        self.cart.add_item(self.product, quantity=2)
        item = CartItem.objects.get(cart=self.cart, product=self.product)
        self.assertEqual(item.quantity, 2)

    def test_add_item_existing(self):
        self.cart.add_item(self.product, quantity=1)
        self.cart.add_item(self.product, quantity=2)
        item = CartItem.objects.get(cart=self.cart, product=self.product)
        self.assertEqual(item.quantity, 3)

    def test_get_total_price(self):
        product2 = Product.objects.create(
            name='iPad', description='Планшет',
            price='599.99', image=get_test_image(),
            category=self.category
        )
        self.cart.add_item(self.product, quantity=2)
        self.cart.add_item(product2, quantity=1)
        self.assertEqual(self.cart.get_total_price(), Decimal('2599.97'))

    def test_get_total_price_empty_cart(self):
        self.assertEqual(self.cart.get_total_price(), 0)


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class OrderTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_order_default_status(self):
        order = Order.objects.create(user=self.user)
        self.assertEqual(order.status, 'new')
        self.assertFalse(order.is_paid)
        self.assertEqual(order.total_price, 0)

    def test_order_status_change(self):
        order = Order.objects.create(user=self.user, status='shipped')
        self.assertEqual(order.status, 'shipped')

    def test_order_str(self):
        order = Order.objects.create(user=self.user)
        self.assertEqual(str(order), f'Заказ №{order.id} — {self.user}')


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class OrderItemTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.category = Category.objects.create(name='Электроника')
        self.product = Product.objects.create(
            name='iPhone', description='Смартфон',
            price='999.99', image=get_test_image(),
            category=self.category
        )
        self.order = Order.objects.create(user=self.user)

    def test_order_item_creation(self):
        item = OrderItem.objects.create(
            order=self.order, product=self.product,
            quantity=2, price='999.99'
        )
        self.assertEqual(item.quantity, 2)
        self.assertEqual(str(item), 'iPhone × 2')


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class StockBalanceTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Электроника')
        self.product = Product.objects.create(
            name='iPhone', description='Смартфон',
            price='999.99', image=get_test_image(),
            category=self.category
        )

    def test_stock_creation(self):
        stock = StockBalance.objects.create(product=self.product, quantity=10)
        self.assertEqual(stock.quantity, 10)
        self.assertEqual(str(stock), 'iPhone — 10 шт.')

    def test_stock_default_quantity(self):
        stock = StockBalance.objects.create(product=self.product)
        self.assertEqual(stock.quantity, 0)


class CustomerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_customer_creation(self):
        customer = Customer.objects.create(
            user=self.user, full_name='Иван Иванов',
            address='ул. Пушкина, д. 10', phone='+79991234567'
        )
        self.assertEqual(customer.full_name, 'Иван Иванов')
        self.assertEqual(customer.phone, '+79991234567')
        self.assertEqual(customer.user, self.user)
        self.assertEqual(str(customer), 'Иван Иванов')
