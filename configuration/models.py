from django.db import models


# class LoanType(models.Model):
#     pass

class Config(models.Model):
    portfolio_value_percentage = models.FloatField(default=0.0)
    loan_interest_rate_percentage = models.FloatField(default=0.0)
    wallet_address = models.CharField(max_length=200, null=True)

    def __str__(self):
        return "Configuration Values"


class Currency(models.Model):
    name = models.CharField(max_length=50, unique=True)
    country = models.CharField(max_length=50)
    rate = models.FloatField(default=0.0)
    buy_rate = models.FloatField(default=0.0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.country} - {self.name}"

    def save(self, *args, **kwargs):

        if self.name:
            self.name = self.name.capitalize()

        if self.country:
            self.country = self.country.capitalize()

        super(Currency, self).save()

    class Meta:
        verbose_name_plural = "Currencies"


class Withdraw(models.Model):
    max = models.FloatField()
    min = models.FloatField()
    # Just didn't want to write these on another model
    addMax = models.FloatField(default=0.0)
    addMin = models.FloatField(default=0.0)
    withdraw_commission = models.FloatField(default=0.0)

    def __str__(self):
        return "Withdraw Values"


