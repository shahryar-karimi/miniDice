from rest_framework import serializers

from user.models import Prediction, CountDown, Player, Referral


class PredictDiceSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Prediction
        fields = ["username", "dice_number1", "dice_number2", "amount", "slot"]

    def get_username(self, obj: Prediction):
        return obj.player.__str__()

    def get_amount(self, obj: Prediction):
        won_count = obj.countdown.get_won_players_count()
        if won_count == 0:
            return 0
        else:
            return round(obj.countdown.amount / won_count, 3)

    def is_valid_predict(self, player, countdown):
        dice_number1 = self.validated_data["dice_number1"]
        dice_number2 = self.validated_data["dice_number2"]
        slot = self.validated_data["slot"]
        if slot > player.predict_slot:
            raise ValueError(f"You don't have slot number {slot}")
        predictions = player.predictions.filter(countdown=countdown, is_active=True)
        for predict in predictions:
            if predict.dice_number1 == dice_number1 and predict.dice_number2 == dice_number2:
                raise ValueError("You've predict this dice before")
            if predict.dice_number1 == dice_number2 and predict.dice_number2 == dice_number1:
                raise ValueError("You've predict this dice before")


class PredictSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = ["slot", "dice_number1", "dice_number2"]


class PredictBoxSerializer(serializers.Serializer):
    predictions = PredictSerializer(many=True)
    slots = serializers.IntegerField()


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


class PlayerUsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ["telegram_username"]


class ReferralSerializer(serializers.ModelSerializer):
    referee = PlayerUsernameSerializer()

    class Meta:
        model = Referral
        fields = ["referee"]


class ReferralsListSerializer(serializers.Serializer):
    referral = ReferralSerializer(many=True)
    count = serializers.SerializerMethodField()

    def get_count(self, obj):
        return obj["referral"].count()


class MissionCheckboxSerializer(serializers.Serializer):
    has_invite = serializers.SerializerMethodField()
    has_submit = serializers.SerializerMethodField()

    def get_has_invite(self, obj: Player):
        return obj.predict_slot > 1

    def get_has_submit(self, obj: Player):
        countdown = CountDown.get_active_countdown()
        return obj.predictions.filter(countdown=countdown, is_active=True).exists()
