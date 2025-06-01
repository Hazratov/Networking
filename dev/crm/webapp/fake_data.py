import os
import sys
import django
import random
from faker import Faker
from datetime import timedelta
from django.utils.timezone import now

# Set up Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

# Import models
from django.contrib.auth.models import User
from webapp.models import Record, Lead, Communication, ActivityLog  # make sure ActivityLog exists

fake = Faker()

def log_activity(user, model_name, object_name, action):
    ActivityLog.objects.create(
        user=user,
        model=model_name,
        object_name=object_name,
        action=action
    )


def create_records(n=50):
    records = []
    users = list(User.objects.all())
    if not users:
        print("❌ No users found. Please create at least one superuser.")
        return []

    for _ in range(n):
        user = random.choice(users)
        record = Record.objects.create(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.unique.email(),
            phone=fake.phone_number(),
            address=fake.address(),
            city=fake.city(),
            province=fake.state(),
            country=fake.country(),
            created_by=user
        )
        records.append(record)
        log_activity(user, "Customer", f"{record.first_name} {record.last_name}", "create")
    return records


def create_leads(records):
    statuses = ['new', 'contacted', 'qualified', 'closed']
    users = list(User.objects.all())

    for record in records:
        assigned_user = random.choice(users)
        lead = Lead.objects.create(
            customer=record,
            status=random.choice(statuses),
            assigned_to=assigned_user,
            note=fake.text(),
            created_at=now() - timedelta(days=random.randint(0, 60))
        )
        log_activity(assigned_user, "Lead", f"{record.first_name} {record.last_name}", "create")


def create_communications(records):
    types = ['call', 'email', 'meeting']
    for record in records:
        for _ in range(random.randint(1, 3)):
            future_days = random.randint(-5, 10)  # 👈 allows both past & future dates
            Communication.objects.create(
                customer=record,
                type=random.choice(types),
                note=fake.text(),
                date=now() + timedelta(days=future_days)  # ✅ future date support
            )
            log_activity(record.created_by, "Communication", f"{record.first_name} {record.last_name}", "communicated")


if __name__ == '__main__':
    print("🚀 Generating fake CRM data...")

    records = create_records(100)
    if records:
        create_leads(records)
        create_communications(records)
        print("✅ Test data created successfully.")
