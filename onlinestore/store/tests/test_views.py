import tempfile
from decimal import Decimal
from io import BytesIO

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from PIL import Image

from store.models import (
    Category, Product, Order, OrderItem, Cart, CartItem,
    StockBalance, Customer
)
from store.services import (
    create_order_from_cart, get_cart_contents, get_user_orders,
    ship_order, check_stock
)

User = get_user_model()

TEST_MEDIA_ROOT = tempfile.mkdtemp()


def get_test_image():
    img = Image.new('RGB', (1, 1), 'white')
    buf = BytesIO()
    img.save(buf, format='PNG')
    return SimpleUploadedFile('test.png', buf.getvalue(), content_type='image/png')


# ===== UNIT-ТЕСТЫ: ИЗОЛИРОВАННЫЕ ФУНКЦИИ =====

@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class CreateOrderFromCartTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.category = Category.objects.create(name='Электроника')
        self.product = Product.objects.create(
            name='iPhone', description='Смартфон', price='999.99',
            image=get_test_image(), category=self.category
        )
        self.stock = StockBalance.objects.create(product=self.product, quantity=10)
        self.cart = Cart.objects.create(user=self.user)
        self.cart.add_item(self.product, quantity=2)

    def test_order_created_with_correct_total(self):
        order = create_order_from_cart(self.cart)
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.status, 'new')
        self.assertEqual(order.total_price, Decimal('1999.98'))

    def test_order_items_created(self):
        order = create_order_from_cart(self.cart)
        items = order.items.all()
        self.assertEqual(items.count(), 1)
        self.assertEqual(items[0].product, self.product)
        self.assertEqual(items[0].quantity, 2)

    def test_stock_reduced(self):
        create_order_from_cart(self.cart)
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantity, 8)

    def test_cart_cleared_after_order(self):
        create_order_from_cart(self.cart)
        self.assertEqual(self.cart.items.count(), 0)


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class GetCartContentsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.category = Category.objects.create(name='Электроника')
        self.product = Product.objects.create(
            name='iPhone', description='Смартфон', price='999.99',
            image=get_test_image(), category=self.category
        )
        self.cart = Cart.objects.create(user=self.user)

    def test_empty_cart(self):
        items, total = get_cart_contents(self.cart)
        self.assertEqual(len(items), 0)
        self.assertEqual(total, 0)

    def test_cart_with_items(self):
        self.cart.add_item(self.product, quantity=3)
        items, total = get_cart_contents(self.cart)
        self.assertEqual(len(items), 1)
        self.assertEqual(total, Decimal('2999.97'))


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class GetUserOrdersTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.other = User.objects.create_user(username='other', password='pass123')

    def test_returns_only_user_orders(self):
        order1 = Order.objects.create(user=self.user, status='new')
        order2 = Order.objects.create(user=self.user, status='shipped')
        order3 = Order.objects.create(user=self.other, status='new')
        orders = get_user_orders(self.user)
        self.assertEqual(orders.count(), 2)
        self.assertIn(order1, orders)
        self.assertIn(order2, orders)
        self.assertNotIn(order3, orders)


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ShipOrderTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.order = Order.objects.create(user=self.user, status='processing')

    def test_status_changed_to_shipped(self):
        ship_order(self.order)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'shipped')


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class CheckStockTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Электроника')
        self.product = Product.objects.create(
            name='iPhone', description='Смартфон', price='999.99',
            image=get_test_image(), category=self.category
        )
        self.stock = StockBalance.objects.create(product=self.product, quantity=5)

    def test_sufficient_stock(self):
        self.assertTrue(check_stock(self.product, 3))

    def test_exact_stock(self):
        self.assertTrue(check_stock(self.product, 5))

    def test_insufficient_stock(self):
        self.assertFalse(check_stock(self.product, 6))

    def test_no_stock_record(self):
        product2 = Product.objects.create(
            name='iPad', description='Планшет', price='599.99',
            image=get_test_image(), category=self.category
        )
        self.assertTrue(check_stock(product2, 100))


# ===== ИНТЕГРАЦИОННЫЕ ТЕСТЫ: ПРЕДСТАВЛЕНИЯ =====

@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ProductListViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Электроника')
        self.product = Product.objects.create(
            name='iPhone', description='Смартфон', price='999.99',
            image=get_test_image(), category=self.category
        )

    def test_product_list_status(self):
        response = self.client.get(reverse('product_list'))
        self.assertEqual(response.status_code, 200)

    def test_product_list_contains_product(self):
        response = self.client.get(reverse('product_list'))
        self.assertContains(response, 'iPhone')

    def test_product_detail_status(self):
        response = self.client.get(reverse('product_detail', args=[self.product.pk]))
        self.assertEqual(response.status_code, 200)


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class CartViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        self.category = Category.objects.create(name='Электроника')
        self.product = Product.objects.create(
            name='iPhone', description='Смартфон', price='999.99',
            image=get_test_image(), category=self.category
        )
        self.stock = StockBalance.objects.create(product=self.product, quantity=10)

    def test_cart_view_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 302)

    def test_cart_view_status(self):
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)

    def test_add_to_cart(self):
        response = self.client.post(reverse('add_to_cart'), {
            'product': self.product.pk,
            'quantity': 2
        })
        self.assertEqual(response.status_code, 302)
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.items.first().quantity, 2)


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class CheckoutViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        self.category = Category.objects.create(name='Электроника')
        self.product = Product.objects.create(
            name='iPhone', description='Смартфон', price='999.99',
            image=get_test_image(), category=self.category
        )
        self.stock = StockBalance.objects.create(product=self.product, quantity=10)
        self.cart = Cart.objects.create(user=self.user)
        self.cart.add_item(self.product, quantity=2)

    def test_checkout_creates_order(self):
        response = self.client.post(reverse('checkout'), {
            'name': 'Иван',
            'address': 'ул. Пушкина',
            'email': 'test@example.com',
            'cart': self.cart.pk
        })
        self.assertEqual(response.status_code, 302)
        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.status, 'new')

    def test_checkout_reduces_stock(self):
        self.client.post(reverse('checkout'), {
            'name': 'Иван',
            'address': 'ул. Пушкина',
            'email': 'test@example.com',
            'cart': self.cart.pk
        })
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantity, 8)

    def test_checkout_clears_cart(self):
        self.client.post(reverse('checkout'), {
            'name': 'Иван',
            'address': 'ул. Пушкина',
            'email': 'test@example.com',
            'cart': self.cart.pk
        })
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.items.count(), 0)
