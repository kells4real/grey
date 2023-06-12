from django.db import models
from authentication.models import User
from wallet.models import Wallet
from django.utils import timezone


class Piggy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    target_amount = models.FloatField(default=0.0)
    save_amount = models.FloatField(default=0.0)
    amount_saved = models.FloatField(default=0.0)
    frequency = models.CharField(max_length=50, default="Weekly",
                                 choices=(("Weekly", "Weekly"), ("Monthly", "Monthly")))
    date = models.DateTimeField(auto_now_add=True)
    updatedDate = models.DateTimeField(default=timezone.now)
    status = models.IntegerField(default=0)
    duration = models.IntegerField(default=0)
    retry = models.BooleanField(default=False)
    incomplete = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} Piggy-{self.id}"

    def size(self):
        return Piggy.objects.filter(user=self.user).count()


