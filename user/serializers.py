from rest_framework import serializers

from user.models import Prediction, CountDownResult


class PredictDiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = ["player", "dice_number1", "dice_number2"]


class WalletAddressSerializer(serializers.Serializer):
    address = serializers.CharField()


class CountDownSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountDownResult
        fields = ["expire_dt", "dice_number1", "dice_number2"]
