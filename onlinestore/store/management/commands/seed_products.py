from django.core.management.base import BaseCommand
from store.models import Category, Product, StockBalance
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO


def create_placeholder_image(size=(200, 200), color=(200, 200, 200)):
    """Создаёт тестовое изображение-заглушку."""
    img = Image.new('RGB', size, color)
    buf = BytesIO()
    img.save(buf, format='JPEG')
    buf.seek(0)
    return ContentFile(buf.read(), name='placeholder.jpg')


class Command(BaseCommand):
    help = 'Добавляет тестовые товары для проверки работы магазина'

    def handle(self, *args, **options):
        categories_data = [
            ('Электроника', 'Гаджеты и техника'),
            ('Одежда', 'Одежда и аксессуары'),
            ('Книги', 'Книги и литература'),
            ('Дом и сад', 'Товары для дома'),
        ]

        for name, description in categories_data:
            cat, created = Category.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            if created:
                self.stdout.write(f'✅ Создана категория: {name}')
            else:
                self.stdout.write(f'⏭️  Категория уже существует: {name}')

        products_data = [
            {
                'name': 'Смартфон Galaxy S24 Ultra',
                'description': 'Флагманский смартфон с камерой 200 Мп, экран 6.8", 256 ГБ, S Pen',
                'price': '109990.00',
                'category': 'Электроника',
                'stock': 15,
                'color': (100, 150, 255),
            },
            {
                'name': 'Ноутбук MacBook Air M3',
                'description': 'Лёгкий и мощный, 13.6" Liquid Retina, 8 ГБ ОЗУ, 256 ГБ SSD, до 18 часов работы',
                'price': '124990.00',
                'category': 'Электроника',
                'stock': 10,
                'color': (150, 150, 200),
            },
            {
                'name': 'Наушники Sony WH-1000XM5',
                'description': 'Беспроводные, с шумоподавлением, 30 часов работы, микросинхронизация',
                'price': '29990.00',
                'category': 'Электроника',
                'stock': 30,
                'color': (50, 50, 50),
            },
            {
                'name': 'Куртка зимняя North Face',
                'description': 'Утеплённая, водонепроницаемая, для температур до -30°C, размеры M–3XL',
                'price': '18990.00',
                'category': 'Одежда',
                'stock': 25,
                'color': (200, 100, 50),
            },
            {
                'name': 'Кроссовки Nike Air Max 90',
                'description': 'Амортизация Air Max, дышащий верх, размеры 36–46',
                'price': '12490.00',
                'category': 'Одежда',
                'stock': 40,
                'color': (255, 255, 255),
            },
            {
                'name': 'Платье летнее хлопковое',
                'description': 'Свободный крой, цветочный принт, размеры XS–L',
                'price': '3990.00',
                'category': 'Одежда',
                'stock': 50,
                'color': (255, 180, 180),
            },
            {
                'name': 'Чистый код',
                'description': 'Роберт Мартин, руководство по гибкому ООП, мягкая обложка',
                'price': '899.00',
                'category': 'Книги',
                'stock': 100,
                'color': (100, 200, 100),
            },
            {
                'name': 'Атомные привычки',
                'description': 'Джеймс Клир, пошаговая методика формирования привычек',
                'price': '749.00',
                'category': 'Книги',
                'stock': 80,
                'color': (200, 150, 100),
            },
            {
                'name': 'Кофемашина DeLonghi Magnifica',
                'description': 'Автоматическая, капучинатор, 1450 Вт, резервуар 1.8 л',
                'price': '42990.00',
                'category': 'Дом и сад',
                'stock': 8,
                'color': (80, 80, 80),
            },
            {
                'name': 'Настольная лампа Xiaomi Mi',
                'description': 'LED, регулировка яркости и цветовой температуры, USB зарядка',
                'price': '2490.00',
                'category': 'Дом и сад',
                'stock': 60,
                'color': (255, 255, 200),
            },
        ]

        for data in products_data:
            category = Category.objects.get(name=data['category'])
            product, created = Product.objects.get_or_create(
                name=data['name'],
                defaults={
                    'description': data['description'],
                    'price': data['price'],
                    'category': category,
                    'image': create_placeholder_image(size=(200, 200), color=data['color']),
                }
            )
            if created:
                self.stdout.write(f'✅ Создан товар: {data["name"]} ({data["price"]} ₽)')
            else:
                self.stdout.write(f'⏭️  Товар уже существует: {data["name"]}')

            stock, stock_created = StockBalance.objects.get_or_create(
                product=product,
                defaults={'quantity': data['stock']}
            )
            if stock_created:
                self.stdout.write(f'   📦 Остаток: {data["stock"]} шт.')
            else:
                self.stdout.write(f'   📦 Остаток уже есть: {stock.quantity} шт.')

        self.stdout.write(self.style.SUCCESS('\n✅ Готово! 10 товаров добавлено.'))
