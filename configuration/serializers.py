from rest_framework import serializers
from .models import *


class CurrencySerializer(serializers.ModelSerializer):

    class Meta:
        model = Currency
        fields = "__all__"


class WithdrawSerializer(serializers.ModelSerializer):

    class Meta:
        model = Withdraw
        fields = "__all__"

