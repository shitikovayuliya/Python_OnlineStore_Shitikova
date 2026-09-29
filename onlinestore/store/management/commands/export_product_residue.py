import json
from django.core.management.base import BaseCommand
from store.models import StockBalance


class Command(BaseCommand):
    help = 'Экспорт остатков товаров в JSON-файл'

    def handle(self, *args, **options):
        balances = StockBalance.objects.select_related('product').all()
        data = []

        for balance in balances:
            data.append({
                'product': balance.product.name,
                'quantity': balance.quantity
            })

        with open('stock_residue.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS(
            f'Остатки экспортированы в файл stock_residue.json ({len(data)} записей)'
        ))

