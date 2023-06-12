from django.db import models
from authentication.models import User


class BankAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_no = models.CharField(max_length=20)
    account_name = models.CharField(max_length=100)
    account_bank = models.CharField(max_length=100)
    primary = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    paystack_key = models.CharField(max_length=200, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.account_name} - {self.account_bank}"

    class Meta:
        verbose_name_plural = "Bank Accounts"


