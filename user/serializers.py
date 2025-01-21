from rest_framework import serializers

from user.models import Prediction


class PredictDiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = ["player",  "dice_number1", "dice_number2"]


class WalletAddressSerializer(serializers.Serializer):
    address = serializers.CharField()
