import django
import os
import asyncio
from asgiref.sync import sync_to_async

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'miniDice.settings')
django.setup()
from user.models import Player, CountDown
from django.conf import settings
from telegram import Bot
from django.utils import timezone


async def get_countdown():
    return await sync_to_async(
        lambda: CountDown.objects.filter(expire_dt__lte=timezone.now()).order_by("-expire_dt").first(),
        thread_sensitive=True)()


async def get_winners(countdown):
    return list(await sync_to_async(
        lambda: list(Player.objects.prefetch_related("predictions").filter(predictions__countdown_id=countdown,
                                                                           predictions__is_win=True)),
        thread_sensitive=True
    )())


async def get_players():
    """Fetch chat IDs asynchronously using Django's ORM in a thread-safe way"""
    countdown = await get_countdown()
    return await get_winners(countdown)


async def broadcast_message():
    """Send message to all stored chat IDs"""
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    players = await get_players()

    for player in players:
        try:
            message = f"""🎉 Congratulations, You’re a Winner! 🎉

Hey {player.first_name}, amazing news! You’ve just won a reward! 💰🔥 Your prize will be sent to your wallet within 24 hours.

But why stop here? There’s more waiting for you! 🚀

🔹 Stay active—more rewards are coming.
🔹 Invite friends—each referral boosts your earnings.
🔹 Submit your results—because every move counts.

Your next reward could be even bigger. Ready to go again? 🎲💸

@dicemaniacs"""
            await bot.send_animation(chat_id=player.telegram_id,
                                     animation="./data/media/camila-cabello-making-it-rain.gif.mp4",
                                     caption=message)
        except Exception as e:
            print(f"Failed to send message to {player.telegram_id}: {e}")


def main():
    asyncio.run(broadcast_message())


if __name__ == '__main__':
    main()
