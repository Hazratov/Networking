from django.contrib.auth.models import User
from django.db import models

class Record(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=255)
    province = models.CharField(max_length=200)
    country = models.CharField(max_length=125)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):

        return self.first_name + "   " + self.last_name


class Lead(models.Model):
    customer = models.ForeignKey(Record, on_delete=models.CASCADE)
    status = models.CharField(choices=[
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('closed', 'Closed')
    ], max_length=20)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Communication(models.Model):
    customer = models.ForeignKey(Record, on_delete=models.CASCADE)
    type = models.CharField(choices=[
        ('call', 'Call'), ('email', 'Email'), ('meeting', 'Meeting')
    ], max_length=20)
    note = models.TextField()
    date = models.DateTimeField(auto_now_add=True)










