import time
from django.db import connections
from django.db.utils import OperationalError
from django.core.management import BaseCommand

class Command(BaseCommand):
    """Django command to pause execution until database is available"""

    def handle(self, *args, **options):
        self.stdout.write('Veritabanı bağlantısı bekleniyor...')
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write('Veritabanına erişilemiyor, 1 saniye sonra tekrar denenecek...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Veritabanı bağlantısı başarılı!'))
