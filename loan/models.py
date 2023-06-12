from django.db import models
from authentication.models import User
from wallet.models import Wallet, AddToWallet
from configuration.models import Currency
from django.utils import timezone

# Create your models here.


class Loan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField(default=0.0)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class LoanApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    amount = models.FloatField(default=0.0)
    date = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(default=False)
    declined = models.BooleanField(default=False)
    confirmed_by = models.CharField(max_length=100, null=True, blank=True)
    confirmDate = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if self.approved:
            currency = Currency.objects.filter(country=self.user.country)
            if currency.exists():
                AddToWallet.objects.create(user=self.user, amount=self.amount, local_currency=currency[0], type="Loan")
            else:
                AddToWallet.objects.create(user=self.user, amount=self.amount, type="Loan")

            Loan.objects.create(user=self.user, amount=self.amount)

        super(LoanApplication, self).save()


