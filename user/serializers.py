from rest_framework import serializers

from user.models import Prediction, CountDown, Player, Referral


class PredictDiceSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Prediction
        fields = ["username", "dice_number1", "dice_number2", "amount"]

    def get_username(self, obj: Prediction):
        return obj.player.telegram_username

    def get_amount(self, obj: Prediction):
        won_count = obj.countdown.get_won_players_count()
        if won_count == 0:
            return 0
        else:
            return round(obj.countdown.amount / won_count, 3)


class WalletAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ["wallet_address"]


class CountDownSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountDown
        fields = ["expire_dt", "dice_number1", "dice_number2", "amount"]


class CountDownTimeSerializer(serializers.ModelSerializer):
    is_finished = serializers.SerializerMethodField()

    class Meta:
        model = CountDown
        fields = ["expire_dt", "amount", "is_active", "is_finished"]

    def get_is_finished(self, obj):
        return obj.is_finished


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ["telegram_id", "telegram_username", "telegram_language_code", "wallet_address"]


class ReferralSerializer(serializers.ModelSerializer):
    class Meta:
        model = Referral
        fields = ["referrer", "referee"]
