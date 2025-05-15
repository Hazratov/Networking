import os
import sys
import django
import random
from faker import Faker

# Django loyihangiz ildiz yo'lini qo'shamiz (manage.py joylashgan papka)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Django sozlamalarini o‘rnatamiz
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')  # settings.py joylashgan loyiha nomi

# Django ni ishga tushirish
django.setup()

from django.contrib.auth.models import User
from webapp.models import Record, Lead, Communication  # model joylashgan papkaga qarab o'zgartiring

fake = Faker()


def create_records(n=10):
    records = []
    users = list(User.objects.all())  # mavjud foydalanuvchilarni olish
    if not users:
        print("❌ Hech qanday foydalanuvchi topilmadi. Avval superuser yarating.")
        return []

    for _ in range(n):
        record = Record.objects.create(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            phone=fake.phone_number(),
            address=fake.address(),
            city=fake.city(),
            province=fake.state(),
            country=fake.country(),
            created_by=random.choice(users)
        )
        records.append(record)
    return records


def create_leads(records):
    statuses = ['new', 'contacted', 'qualified', 'closed']
    users = list(User.objects.all())
    for record in records:
        Lead.objects.create(
            customer=record,
            status=random.choice(statuses),
            assigned_to=random.choice(users),
            note=fake.paragraph()
        )


def create_communications(records):
    types = ['call', 'email', 'meeting']
    for record in records:
        for _ in range(random.randint(1, 3)):  # har bir mijoz uchun 1-3 aloqa
            Communication.objects.create(
                customer=record,
                type=random.choice(types),
                note=fake.text()
            )


if __name__ == '__main__':
    print("📦 Mavjud foydalanuvchilar bilan test ma'lumotlari yaratilmoqda...")
    records = create_records(10)
    if records:
        create_leads(records)
        create_communications(records)
        print("✅ Sun'iy ma'lumotlar yaratildi.")
