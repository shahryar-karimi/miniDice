from import_export import resources
from .models import Player


class PlayerResource(resources.ModelResource):
    class Meta:
        model = Player
        fields = ['telegram_id', 'telegram_username', 'first_name', 'last_name', 'wallet_address', 'wallet_insert_dt']
