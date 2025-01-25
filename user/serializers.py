from rest_framework import serializers

from user.models import Prediction, CountDown, Player


class PredictDiceSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    class Meta:
        model = Prediction
        fields = ["username", "dice_number1", "dice_number2", "amount"]

    def get_username(self, obj: Prediction):
        return obj.player.telegram_username

    def get_amount(self, obj: Prediction):
        return obj.countdown.amount


class WalletAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ["wallet_address"]

    def create(self, validated_data):
        pass


class CountDownSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountDown
        fields = ["expire_dt", "dice_number1", "dice_number2", "amount"]


class CountDownTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountDown
        fields = ["expire_dt", "amount"]


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ["telegram_id", "telegram_username", "telegram_language_code", "wallet_address"]
