import django
import os
import asyncio
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
    )
    
    print(f"Found {len(players_with_at_least_one_prediction)} players with at least one prediction")
    
    alireza = await sync_to_async(list)(Player.objects.filter(telegram_id=426083623))    
    return alireza
    
    # return players_with_at_least_one_prediction

async def broadcast_message():
    """Send message to all stored chat IDs"""
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    players = await get_players()

    for player in players:
        try:
            
            message = f"""Hey Dear {player.first_name}, Loyal Citizen of Dice Maniacs! 👑

📢 Citizens of Dice Maniacs, Let’s Unlock Bigger Rewards! 🚀

Did you know that once our community reaches 8,000 members, the daily rewards will DOUBLE? 💰🔥

That means more excitement, bigger prizes, and even more joy with every roll! 🎲

We’re getting closer—keep referring, spread the word, and let’s make it happen! 💪🚀

🔗 Invite now & be part of the next big level!

@dicemaniacs
"""
            await bot.send_photo(chat_id=player.telegram_id, photo="./data/media/Dice-Maniacs-Placement.jpg", caption=message)
            # await bot.send_video(chat_id=player.telegram_id, video="./data/media/Trump_meme.MOV", caption=message)
        except Exception as e:
            print(f"Failed to send message to {player.telegram_id}: {e}")


def main():
    asyncio.run(broadcast_message())


if __name__ == '__main__':
    main()
