from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Wallet)
admin.site.register(WalletTransfer)
admin.site.register(AddToWallet)
admin.site.register(Withdraw)
admin.site.register(CryptoAdd)


