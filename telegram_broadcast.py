import asyncio
import os
from datetime import timedelta

import django
from asgiref.sync import sync_to_async
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'miniDice.settings')
django.setup()
from user.models import Player
from django.conf import settings
from telegram import Bot


async def get_players():
    three_days_ago_midnight = (timezone.now() - timedelta(days=3)).replace(hour=0, minute=0, second=0, microsecond=0)
    selected_players = await sync_to_async(list)(
        Player.objects.filter(referrals__insert_dt__gt=three_days_ago_midnight)
    )
    return selected_players


async def get_all_players():
    return await sync_to_async(list)(Player.objects.all().order_by('telegram_id'))


async def get_non_russian():
    return await sync_to_async(list)(Player.objects.all().exclude(telegram_language_code="ru").order_by('telegram_id'))


async def get_russian():
    return await sync_to_async(list)(Player.objects.filter(telegram_language_code="ru").order_by('telegram_id'))


async def broadcast_message():
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    players = await get_players()
    for player in players:
        try:
            message = f"""🎉Hello, NEW Dice Maniacs Citizen! 🎲

You’ve joined through a recommendation, and we’ve got AMAZING things waiting for you in Dice Land! 🌍✨

🚨$20 Retention Bonus and $30 Referral Bonus are just the beginning! And don’t forget about the $100 prize every night! 💰🔥

Connect your wallet to start your adventure and claim your rewards! 🔗🚀

Come back and join the fun—the experience is just starting! 🎉🎲"""
            await bot.send_photo(chat_id=player.telegram_id, photo="./data/media/5904615795118425431.jpg",
                                 caption=message)
            # await bot.send_video(chat_id=player.telegram_id, video="./data/media/Trump_meme.MOV", caption=message)
        except Exception as e:
            print(f"Failed to send message to {player.telegram_id}: {e}")


def main():
    asyncio.run(broadcast_message())


if __name__ == '__main__':
    main()
