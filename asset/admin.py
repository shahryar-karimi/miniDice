from django.contrib import admin
import time
from asset.models import Asset
from user.models import Player
from services.ton_services import get_balance


# Register your models here.
@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ["player", "symbol", "balance", "update_dt"]
    list_filter = ["symbol"]
    search_fields = ["player__telegram_id", "player__telegram_username", "player__first_name"]
    actions = ["sync_assets"]

    def sync_assets(self, request, queryset):
        players = Player.objects.filter(wallet_address__isnull=False)
        for player in players:
            time.sleep(10)
            assets = get_balance(player.wallet_address)
            for asset, balance in assets.items():
                create_asset, is_created = Asset.objects.get_or_create(symbol=asset, player=player)
                create_asset.balance = balance
                create_asset.save(update_fields=["balance"])
