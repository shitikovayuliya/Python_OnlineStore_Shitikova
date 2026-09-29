from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Загрузка товаров и остатков из JSON-файла'

    def handle(self, *args, **options):
        self.stdout.write('Загрузка данных из fixtures/data.json...')
        call_command('loaddata', 'data.json', app_label='store')
        self.stdout.write(self.style.SUCCESS('Данные успешно загружены!'))
