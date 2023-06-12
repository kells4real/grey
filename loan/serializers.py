from rest_framework import serializers
from .models import LoanApplication, Loan


class LoanApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = LoanApplication
        fields = ("amount",)


class LoanListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField("get_user")

    class Meta:
        model = LoanApplication
        fields = "__all__"

    def get_user(self, obj):
        return {"name": f"{obj.user.first_name} {obj.user.last_name}",
                "wallet": obj.user.wallet.balance, "username": obj.user.username}


class LoanSerializer(serializers.ModelSerializer):

    class Meta:
        model = Loan
        fields = "__all__"


class LoanCrudSerializer(serializers.ModelSerializer):

    class Meta:
        model = LoanApplication
        fields = ("approved", "declined")
