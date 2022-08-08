from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    balance = models.PositiveIntegerField(default=20000)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.user.username,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email,
            "phone": self.phone,
            "address": self.address,
            "balance": self.balance
        }

    def deposit(self, amount):
        self.balance += amount
        self.save()

    def spend(self, amount):
        self.balance -= amount
        if self.balance < 0:
            raise ValueError("موجودی منفی قابل قبول نیست")
        self.save()
