from django.db import models
from authentication.models import User
from configuration.models import Currency
from django.utils import timezone
from authentication.utils import Util


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.FloatField(default=0.0)

    def __str__(self):
        return self.user.username


class WalletTransfer(models.Model):
    user_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_from')
    user_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_to')
    amount = models.FloatField()
    date = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
        return f"{self.user_from} - {self.user_to} - {self.amount}"

    def save(self, *args, **kwargs):
        if self.amount:
            to_wallet = Wallet.objects.get(user=self.user_to)
            from_wallet = Wallet.objects.get(user=self.user_from)

            to_wallet.balance += self.amount
            from_wallet.balance -= self.amount
            to_wallet.save(update_fields=['balance'])
            from_wallet.save(update_fields=['balance'])
        super(WalletTransfer, self).save()


class AddToWallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    amount = models.FloatField(db_index=True)
    local_currency = models.ForeignKey(Currency, on_delete=models.DO_NOTHING, null=True, blank=True)
    type = models.CharField(max_length=50, default="Transfer",
                            choices=(("Transfer", "Transfer"), ("Referral", "Referral"), ("Loan", "Loan"),
                                     ("Bitcoin", "Bitcoin")))
    referral = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="referral")
    converted_amount = models.FloatField(default=0.0)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.amount}"

    def save(self, *args, **kwargs):
        if self.amount > 0:
            wallet = Wallet.objects.get(user=self.user)
            wallet.balance += self.amount
            wallet.save(update_fields=['balance'])
        if not self.converted_amount and self.type == "Transfer":
            self.converted_amount = self.local_currency.rate * self.amount
        elif not self.converted_amount and self.type == "Referral":
            rate = Currency.objects.filter(country=self.user.country)
            if rate.exists():
                self.converted_amount = rate[0].buy_rate * self.amount
        super(AddToWallet, self).save()

    class Meta:
        verbose_name_plural = "Add to Wallet"


class Withdraw(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    amount = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=50, default="Transfer",
                            choices=(("Local", "Local"), ("Bitcoin", "Bitcoin"), ("Bank Transfer", "Bank Transfer"),
                                     ("Paypal", "Paypal")), db_index=True)
    approved = models.BooleanField(default=False)
    declined = models.BooleanField(default=False)
    confirmed_by = models.CharField(max_length=100, null=True, blank=True)
    confirmDate = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if self.amount and not self.approved and not self.declined:
            wallet = Wallet.objects.get(user=self.user)
            wallet.balance -= self.amount
            wallet.save(update_fields=['balance'])
        if self.declined:
            wallet = Wallet.objects.get(user=self.user)
            wallet.balance += self.amount
            wallet.save(update_fields=['balance'])
        super(Withdraw, self).save()


class CryptoAdd(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    amount = models.FloatField()
    approved = models.BooleanField(default=False)
    declined = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    ref = models.TextField()
    confirmedBy = models.CharField(null=True, blank=True, max_length=100)
    type = models.CharField(max_length=50, default="Bitcoin",
                            choices=(("Ethereum", "Ethereum"), ("Bitcoin Cash", "Bitcoin Cash"),
                                     ("Bitcoin", "Bitcoin")))

    def __str__(self):
        return self.user.username + " " + str(self.amount)

    def save(self, *args, **kwargs):
        if self.approved:
            AddToWallet.objects.create(user=self.user, amount=self.amount, type="Bitcoin")
            email_body = f"Hi {self.user.username}, your bitcoin deposit of ${self.amount} " \
                         f"has been confirmed and added to your wallet. " \
                         f"Thank you for investing with Cighedge. " \
                         f" Have a wonderful day. \n "
            data = {'email_body': email_body, 'to_email': self.user.email,
                    'email_subject': 'Bitcoin Deposit Confirmed'}
            Util.send_email(data)

        if self.declined:
            email_body = f"Hi {self.user.username}, your bitcoin deposit of ${self.amount} " \
                         f"has been declined due to some irregularities in your transaction. " \
                         f"If you feel this is wrong, please contact support for assistance." \
                         f"Thank you for investing with Cighedge. " \
                         f" Have a wonderful day. \n "
            data = {'email_body': email_body, 'to_email': self.user.email,
                    'email_subject': 'Bitcoin Deposit Declined'}
            Util.send_email(data)

        super(CryptoAdd, self).save()
