from rest_framework import serializers
from .models import BankAccount


class BankAccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = BankAccount
        fields = ("id", "account_no", "account_name", "account_bank", "primary", "date", "updated", "paystack_key")


class BankAccountUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = BankAccount
        fields = ("primary",)

