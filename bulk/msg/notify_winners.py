import django
import os
import asyncio
from asgiref.sync import sync_to_async

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'miniDice.settings')
django.setup()
from user.models import Player, CountDown
from django.conf import settings
from telegram import Bot


async def get_players():
    """Fetch chat IDs asynchronously using Django's ORM in a thread-safe way"""
    countdown: CountDown = CountDown.get_last_countdown()
    return sync_to_async(Player.objects.select_related("prediction")
                         .filter(predictions__countdown_id=countdown,
                                 predictions__is_win=True))


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
            await bot.send_animation(chat_id=player.telegram_id, animation="./data/media/Trump_meme.MOV", caption=message)
        except Exception as e:
            print(f"Failed to send message to {player.telegram_id}: {e}")


def main():
    asyncio.run(broadcast_message())


if __name__ == '__main__':
    main()
