from .models import Piggy
from rest_framework import serializers


class PiggyCrudSerializer(serializers.ModelSerializer):

    class Meta:
        model = Piggy
        fields = ("target_amount", "save_amount", "frequency", "duration")


class PiggySerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField("get_user")

    class Meta:
        model = Piggy
        fields = "__all__"

    def get_user(self, obj):
        return {"username": obj.user.username, "fullname": f"{obj.user.first_name} {obj.user.last_name}"}
