import asyncio
import os

import django
from asgiref.sync import sync_to_async

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'miniDice.settings')
django.setup()
from user.models import Player
from django.conf import settings
from telegram import Bot

from django.db.models import Count


# Asynchronously fetch players who have at least one prediction
async def get_players():
    """Fetch players with at least one prediction asynchronously using Django's ORM in a thread-safe way"""
    # Use Django ORM to filter players that have at least one related prediction
    players_with_at_least_one_prediction = await sync_to_async(list)(
        Player.objects.annotate(prediction_count=Count('predictions'))  # Annotate player with the count of predictions
        .filter(prediction_count__gt=0)  # Only players with at least one prediction
        .order_by('telegram_id')
    )

    return players_with_at_least_one_prediction


async def get_all_players():
    return await sync_to_async(list)(Player.objects.all().order_by('telegram_id'))


async def get_non_russian():
    return await sync_to_async(list)(Player.objects.all().exclude(telegram_language_code="ru").order_by('telegram_id'))


async def get_russian():
    return await sync_to_async(list)(Player.objects.filter(telegram_language_code="ru").order_by('telegram_id'))


async def broadcast_message():
    """Send message to all stored chat IDs"""
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    players = await get_russian()
    for player in players:
        try:
            message = f"""🚀Что-то захватывающее скоро появится в вашем кошельке! 💰✨

Вы один из первых, кто станет частью чего-то грандиозного, что вот-вот произойдёт в мире кубиков! 🎲

Если вы ещё не подключили свой кошелёк, самое время сделать это!

🔗Подключите кошелёк СЕЙЧАС, пока не стало слишком поздно!⏳"""
            await bot.send_photo(chat_id=player.telegram_id, photo="./data/media/flying-to-dice-land.jpg",
                                 caption=message)
            # await bot.send_video(chat_id=player.telegram_id, video="./data/media/Trump_meme.MOV", caption=message)
        except Exception as e:
            print(f"Failed to send message to {player.telegram_id}: {e}")


def main():
    asyncio.run(broadcast_message())


if __name__ == '__main__':
    main()
