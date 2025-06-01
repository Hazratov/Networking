from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from webapp.models import Record, Lead, Communication
from django.utils.timezone import now, timedelta

class CRMTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.record = Record.objects.create(
            first_name='John', last_name='Doe', email='john@example.com',
            phone='1234567890', address='123 St', city='Tashkent',
            province='Tashkent', country='UZ', created_by=self.user
        )
        self.lead = Lead.objects.create(
            customer=self.record, status='new', assigned_to=self.user, note='Test Lead'
        )
        self.communication = Communication.objects.create(
            customer=self.record, type='call', note='Follow up', date=now()
        )

    def login(self):
        self.client.login(username='testuser', password='testpass')

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_register_user(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'testuser',
                'email': 'testuser@example.com',
                'password1': 'ComplexPassword123',
                'password2': 'ComplexPassword123',
            },
            follow=True  # redirectni kuzatadi
        )

        self.assertEqual(response.status_code, 200) # yoki 302 agar redirect bo‘lsa

    def test_login_user(self):
        response = self.client.post(reverse('my-login'), {
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(response.status_code, 302)

    def test_dashboard_access(self):
        self.login()
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_create_record_page(self):
        self.login()
        response = self.client.get(reverse('create-record'))
        self.assertEqual(response.status_code, 200)

    def test_create_record_post(self):
        self.login()
        response = self.client.post(reverse('create-record'), {
            'first_name': 'Alice', 'last_name': 'Smith', 'email': 'alice@example.com',
            'phone': '998998998', 'address': 'X St', 'city': 'Bukhara',
            'province': 'Bukhara', 'country': 'UZ'
        })
        self.assertEqual(response.status_code, 302)

    def test_update_record(self):
        self.login()
        response = self.client.post(reverse('update-record', args=[self.record.id]), {
            'first_name': 'Updated',
            'last_name': self.record.last_name,
            'email': self.record.email,
            'phone': self.record.phone,
            'address': self.record.address,
            'city': self.record.city,
            'province': self.record.province,
            'country': self.record.country
        })
        self.assertEqual(response.status_code, 302)

    def test_delete_record(self):
        self.login()
        response = self.client.get(reverse('delete-record', args=[self.record.id]))
        self.assertEqual(response.status_code, 302)

    def test_view_record(self):
        self.login()
        response = self.client.get(reverse('record', args=[self.record.id]))
        self.assertEqual(response.status_code, 200)

    def test_create_lead_page(self):
        self.login()
        response = self.client.get(reverse('create-lead'))
        self.assertEqual(response.status_code, 200)

    def test_update_lead_page(self):
        self.login()
        response = self.client.get(reverse('update-lead', args=[self.lead.id]))
        self.assertEqual(response.status_code, 200)

    def test_leads_table(self):
        self.login()
        response = self.client.get(reverse('leads-table'))
        self.assertEqual(response.status_code, 200)

    def test_create_communication_page(self):
        self.login()
        response = self.client.get(reverse('create-communication'))
        self.assertEqual(response.status_code, 200)

    def test_update_communication_page(self):
        self.login()
        response = self.client.get(reverse('update-communication', args=[self.communication.id]))
        self.assertEqual(response.status_code, 200)

    def test_customers_table_view(self):
        self.login()
        response = self.client.get(reverse('customers-table'))
        self.assertEqual(response.status_code, 200)

    def test_communications_table_view(self):
        self.login()
        response = self.client.get(reverse('communications-table'))
        self.assertEqual(response.status_code, 200)

    def test_logout_user(self):
        self.login()
        response = self.client.get(reverse('user-logout'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_kpis_exist(self):
        self.login()
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, 'Total Customers')

    def test_lead_conversion_percentage_calculated(self):
        self.login()
        response = self.client.get(reverse('dashboard'))
        self.assertIn('lead_conversion_rate', response.context)
