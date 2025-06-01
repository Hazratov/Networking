import os
import sys
import django
import random
from faker import Faker
from datetime import timedelta
from django.utils.timezone import now

# Django sozlash
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

# Modellarni chaqirish
from django.contrib.auth.models import User
from webapp.models import Record, Lead, Communication, ActivityLog

fake = Faker()


def log_bulk_activities(logs):
    """Activity loglarni samarali bulk orqali qo‘shish"""
    ActivityLog.objects.bulk_create(logs, batch_size=1000)


def create_records(n=10000):
    users = list(User.objects.all())
    if not users:
        print("❌ Hech qanday foydalanuvchi topilmadi. Avval superuser yarating.")
        return []

    records = []
    activity_logs = []

    for _ in range(n):
        user = random.choice(users)
        first_name = fake.first_name()
        last_name = fake.last_name()
        record = Record(
            first_name=first_name,
            last_name=last_name,
            email=f"{first_name.lower()}.{last_name.lower()}{random.randint(1000, 9999)}@example.com",
            phone=fake.phone_number(),
            address=fake.address(),
            city=fake.city(),
            province=fake.state(),
            country=fake.country(),
            created_by=user
        )
        records.append(record)
        activity_logs.append(ActivityLog(
            user=user,
            model="Customer",
            object_name=f"{first_name} {last_name}",
            action="create"
        ))

    created_records = Record.objects.bulk_create(records, batch_size=500)
    log_bulk_activities(activity_logs)
    return created_records


def create_leads(records):
    users = list(User.objects.all())
    statuses = ['new', 'contacted', 'qualified', 'closed']

    leads = []
    logs = []

    for record in records:
        assigned_user = random.choice(users)
        lead = Lead(
            customer=record,
            status=random.choice(statuses),
            assigned_to=assigned_user,
            note=fake.text(),
            created_at=now() - timedelta(days=random.randint(0, 60))
        )
        leads.append(lead)
        logs.append(ActivityLog(
            user=assigned_user,
            model="Lead",
            object_name=f"{record.first_name} {record.last_name}",
            action="create"
        ))

    Lead.objects.bulk_create(leads, batch_size=500)
    log_bulk_activities(logs)


def create_communications(records):
    types = ['call', 'email', 'meeting']
    communications = []
    logs = []

    for record in records:
        for _ in range(random.randint(1, 2)):
            comm_type = random.choice(types)
            comm = Communication(
                customer=record,
                type=comm_type,
                note=fake.text(),
                date=now() + timedelta(days=random.randint(-5, 10))
            )
            communications.append(comm)
            logs.append(ActivityLog(
                user=record.created_by,
                model="Communication",
                object_name=f"{record.first_name} {record.last_name}",
                action="communicated"
            ))

    Communication.objects.bulk_create(communications, batch_size=500)
    log_bulk_activities(logs)


if __name__ == '__main__':
    print("🚀 Fake CRM ma'lumotlari yaratilmoqda...")
    records = create_records(1000)
    if records:
        create_leads(records)
        create_communications(records)
        print("✅ Ma'lumotlar muvaffaqiyatli yaratildi.")
    else:
        print("⚠️ Foydalanuvchilar yo‘qligi sababli hech narsa yaratilmadi.")
