from django.contrib import admin

from asset.models import Asset
from services.ton_services import get_balance
from user.models import Player


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ["player", "symbol", "balance", "decimal", "price", "usd_value", "update_dt"]
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
            for master_address, value in assets.items():
                create_asset, is_created = Asset.objects.get_or_create(master_address=master_address, player=player)
                create_asset.balance = value.get("balance")
                create_asset.decimal = value.get("decimal")
                create_asset.price = value.get("price")
                create_asset.name = value.get("name")
                create_asset.symbol = value.get("symbol")
                create_asset.save(update_fields=["balance", "decimal", "price", "name", "symbol"])
