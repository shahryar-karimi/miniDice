import os, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'miniDice.settings')
django.setup()

from user.models import Player
from asset.models import Asset
from services.ton_services import get_balance


def sync_assets():
    Asset.objects.all().delete()
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


def main():
    sync_assets()


if __name__ == '__main__':
    main()
