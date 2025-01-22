from rest_framework import serializers

from user.models import Prediction, CountDown, Player


class PredictDiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = ["player", "dice_number1", "dice_number2"]


class WalletAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ["wallet_address"]

    def create(self, validated_data):
        pass


class CountDownSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountDown
        fields = ["expire_dt", "dice_number1", "dice_number2"]


class CountDownTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountDown
        fields = ["expire_dt"]


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ["telegram_id", "telegram_username", "telegram_language_code", "wallet_address"]


class WinnersListSerializer(serializers.Serializer):
    predictions = PredictDiceSerializer(many=True)
