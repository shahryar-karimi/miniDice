import django
import os
import asyncio
from asgiref.sync import sync_to_async

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'miniDice.settings')
django.setup()
from user.models import Player
from django.conf import settings
from telegram import Bot


async def get_players():
    """Fetch chat IDs asynchronously using Django's ORM in a thread-safe way"""
    return await sync_to_async(list)(Player.objects.filter(wallet_address__isnull=False))


async def broadcast_message():
    """Send message to all stored chat IDs"""
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    players = await get_players()

    for player in players:
        try:
            message = f"""Hey {player.first_name}, did you know you’re just one step away from a guaranteed chance to win?

✔️ Play once and you’re automatically in for a $20 daily lottery! 🎲
✔️ Submit your results or refer a friend to boost your chances even more!
✔️  Refer 21 people and guess what? You become a GUARANTEED WINNER—no luck needed!  🎯💸

Don’t let this free money slip away. Make your move NOW! 🚀💰"""
            await bot.send_video(chat_id=player.telegram_id, video="./data/media/Trump_meme.MOV", caption=message)
        except Exception as e:
            print(f"Failed to send message to {player.telegram_id}: {e}")


def main():
    asyncio.run(broadcast_message())


if __name__ == '__main__':
    main()
