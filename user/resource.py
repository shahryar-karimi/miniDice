from import_export import resources
from import_export.fields import Field

from .models import Player, Prediction, Referral


class PlayerResource(resources.ModelResource):
    class Meta:
        model = Player
        fields = ['telegram_id', 'telegram_username', 'first_name', 'last_name', 'wallet_address', 'wallet_insert_dt']


class PredictionResource(resources.ModelResource):
    wallet = Field(dehydrate_method="dehydrate_wallet")
    amount = Field(dehydrate_method="dehydrate_amount")

    class Meta:
        model = Prediction
        fields = ["player", "insert_dt", "countdown", "dice_number1", "dice_number2", "slot", "is_win", "is_active"]

    def dehydrate_wallet(self, obj: Prediction):
        if obj.player.wallet_address:
            return obj.player.wallet_address
        return "-"

    def dehydrate_amount(self, obj: Prediction):
        if obj.is_win:
            countdown = obj.countdown
            return countdown.amount / countdown.get_won_players_count()
        return 0

class ReferralResource(resources.ModelResource):
    class Meta:
        model = Referral
        fields = ['referrer', 'referee', 'insert_dt']