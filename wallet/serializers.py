from rest_framework import serializers
from .models import Wallet, WalletTransfer, Withdraw, AddToWallet, CryptoAdd
from authentication.serializers import UserDetailSerializer
from authentication.models import User


class WalletSerializer(serializers.ModelSerializer):

    class Meta:
        model = Wallet
        fields = ("amount",)


class WalletTransferSerializer(serializers.ModelSerializer):
    user_from = serializers.SerializerMethodField("get_user_from")
    user_to = serializers.SerializerMethodField("get_user_to")

    class Meta:
        model = WalletTransfer
        fields = ("id", "user_from", "user_to", "amount", "date")

    def get_user_from(self, obj):
        return obj.user_from.username

    def get_user_to(self, obj):
        return obj.user_to.username


class WalletTransferCreateSerializer(serializers.Serializer):
    amount = serializers.FloatField()
    user = serializers.CharField()
    otp = serializers.CharField()


class AddToWalletSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField("get_user")

    class Meta:
        model = AddToWallet
        fields = "__all__"

    def get_user(self, obj):
        return obj.user.username


class CRUDAddToWalletSerializer(serializers.Serializer):
    amount = serializers.FloatField()
    local_currency = serializers.CharField(max_length=50)
    type = serializers.CharField(max_length=50)
    shield = serializers.CharField(max_length=200)


class WithdrawSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField('get_user')

    class Meta:
        model = Withdraw
        fields = ("id", "user", "amount", "date", "type", 'approved', 'declined', 'confirmed_by', 'confirmDate')

    def get_user(self, obj):
        return {"name": f"{obj.user.first_name} {obj.user.last_name}",
                "wallet": obj.user.wallet.balance, "username": obj.user.username}


class WithdrawCrudSerializer(serializers.ModelSerializer):

    class Meta:
        model = Withdraw
        fields = ("amount", "type")


class WithdrawUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdraw
        fields = ("approved", "declined")


class CryptoAddSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField("getUser")

    class Meta:
        model = CryptoAdd
        fields = "__all__"

    def getUser(self, obj):
        user = UserDetailSerializer(obj.user, many=False)
        return user.data


class CryptoAddCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CryptoAdd
        fields = ("amount", "ref")




