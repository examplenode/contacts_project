import sqlite3
import os
from django.core.management.base import BaseCommand
from contacts.models import Contact

class Command(BaseCommand):
    help = 'Переносит контакты из старой SQLite базы в новую PostgreSQL'

    def handle(self, *args, **options):
        sqlite_path = os.path.join(os.getcwd(), 'db.sqlite3')
        
        if not os.path.exists(sqlite_path):
            self.stdout.write(self.style.ERROR(f'Файл {sqlite_path} не найден!'))
            return

        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contacts_contact';")
        if not cursor.fetchone():
            self.stdout.write(self.style.WARNING('В SQLite нет таблицы contacts_contact.'))
            return

        cursor.execute("SELECT name, phone, email, category FROM contacts_contact")
        rows = cursor.fetchall()
        
        created_count = 0
        for row in rows:
            name, phone, email, category = row
            obj, created = Contact.objects.get_or_create(
                email=email,
                phone=phone,
                defaults={
                    'name': name,
                    'category': category
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Добавлен: {name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Пропущен (уже есть): {name}'))
        
        conn.close()
        self.stdout.write(self.style.SUCCESS(f'Готово! Перенесено {created_count} контактов.'))