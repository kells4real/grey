from rest_framework import serializers
from .models import *
from django.db.models import Sum, Q
from wallet.models import Withdraw, AddToWallet, WalletTransfer, Wallet
from wallet.serializers import WalletTransferSerializer, WithdrawSerializer, AddToWalletSerializer


class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = "__all__"


class AdminInvestmentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField('get_user')
    portfolio = serializers.SerializerMethodField('get_portfolio')

    class Meta:
        model = Investment
        fields = ('user', 'portfolio', 'amount', 'date', 'last_profit_date')

    def get_user(self, obj):
        return obj.user.username

    def get_portfolio(self, obj):
        return obj.portfolio.name


class InvestmentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField('get_user')
    portfolio = serializers.SerializerMethodField('get_portfolio')
    profit = serializers.SerializerMethodField('get_profit')

    class Meta:
        model = Investment
        fields = ('id', 'user', 'portfolio', 'amount', 'date', 'last_profit_date', 'profit', 'sold', 'disabled')

    def get_user(self, obj):
        return obj.user.username

    def get_portfolio(self, obj):
        return obj.portfolio.name

    def get_profit(self, obj):
        profit = Profit.objects.filter(user=obj.user, investment=obj)
        return sum(profit.values_list('amount', flat=True))


class ProfitSerializer(serializers.ModelSerializer):
    investment = serializers.SerializerMethodField('getInvestment')

    class Meta:
        model = Profit
        fields = ('id', 'amount', 'date', 'investment')

    def getInvestment(self, obj):
        return obj.investment.portfolio.name


class InvestSerializer(serializers.Serializer):
    portfolio = serializers.CharField(max_length=100)
    amount = serializers.FloatField()


class ReferralSerializer(serializers.ModelSerializer):
    total_investments = serializers.SerializerMethodField("total_investment")

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email", "gender", "mobile_no", "image", "is_verified",
                  "total_investments", "date_joined", "username")

    def total_investment(self, obj):
        return Investment.objects.filter(user=obj).count()


class SoldInvestmentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField('getUser')

    class Meta:
        model = SoldInvestment
        fields = "__all__"

    def getUser(self, obj):
        return {
            'username': obj.user.username,
            'name': f"{obj.user.first_name} {obj.user.last_name}"
        }
