from django.db import models
from authentication.models import User
from wallet.models import Wallet
from django.utils import timezone
from wallet.models import AddToWallet
from configuration.models import Config


def percentage(percentage_value, total_value):
    return (percentage_value / 100) * total_value


class Portfolio(models.Model):
    name = models.CharField(max_length=100, unique=True)
    lowest = models.FloatField(default=0.0)
    highest = models.FloatField(default=0.0)
    date = models.DateTimeField(auto_now_add=True)
    interest_percentage = models.FloatField(default=0.0)
    profit_frequency = models.CharField(max_length=50,
                                        default="Monthly", choices=(("Weekly", "Weekly"), ("Monthly", "Monthly"),
                                                                    ("90 Days", "90 Days"), ("180 Days", "180 Days"),
                                                                    ("365 Days", "365 Days")))

    def __str__(self):
        return self.name


class Investment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    amount = models.FloatField(default=0.0, db_index=True)
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    disabled = models.BooleanField(default=False)
    sold = models.BooleanField(default=False)
    last_profit_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.email} - {self.portfolio.name}"

    def interest(self):
        return percentage(self.portfolio.interest_percentage, self.amount)

    def value(self):
        return percentage(60, self.amount)

    def save(self, *args, **kwargs):

        # Try to give referral bonus if the user hasn't already been given
        if self.user.referee:
            if not AddToWallet.objects.filter(user=self.user.referee, type="Referral", referral=self.user).exists():
                AddToWallet.objects.create(user=self.user.referee, type="Referral", referral=self.user,
                                           amount=percentage(10, self.amount))
        super(Investment, self).save()


class Profit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE)
    amount = models.FloatField(default=0.0, db_index=True)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if self.amount > 0:
            wallet = Wallet.objects.get(user=self.user)
            wallet.balance += self.amount
            wallet.save(update_fields=['balance'])
        super(Profit, self).save()


class SoldInvestment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE)
    amount = models.FloatField(default=0.0, db_index=True)
    date = models.DateTimeField(default=timezone.now)
    confirmedBy = models.CharField(null=True, blank=True, max_length=100, editable=False)
    approved = models.BooleanField(default=False)
    declined = models.BooleanField(default=False)
    confirmDate = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username + ' ' + self.investment.portfolio.name

    def save(self, *args, **kwargs):
        config = Config.objects.all().first()
        if not self.amount:
            self.amount = percentage(config.portfolio_value_percentage, self.investment.amount)
        if self.approved:
            investment = self.investment
            investment.sold = True
            investment.save(update_fields=['sold'])
            wallet = Wallet.objects.get(user=self.user)
            wallet.balance += self.amount
            wallet.save(update_fields=['balance'])
        if self.declined:
            investment = self.investment
            investment.disabled = False
            investment.save(update_fields=['disabled'])

        super(SoldInvestment, self).save()
