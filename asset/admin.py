from django.contrib import admin
import time
from asset.models import Asset
from user.models import Player
from services.ton_services import get_balance


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ["player", "symbol", "balance", "decimal", "update_dt"]
    list_filter = ["symbol"]
    search_fields = ["player__telegram_id", "player__telegram_username", "player__first_name"]
    actions = ["sync_assets"]

    def sync_assets(self, request, queryset):
        players = Player.objects.filter(wallet_address__isnull=False)
        for player in players:
            assets = {}
            for i in range(10):
                try:
                    assets = get_balance(player.wallet_address)
                    break
                except Exception as e:
                    print(e)
            for asset, value in assets.items():
                create_asset, is_created = Asset.objects.get_or_create(symbol=asset, player=player)
                create_asset.balance = value.get("balance")
                create_asset.decimal = value.get("decimal")
                create_asset.save(update_fields=["balance", "decimal"])
