import asyncio
import csv
import os
from pathlib import Path

import django
from asgiref.sync import sync_to_async
from telegram import Bot

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'miniDice.settings')
django.setup()
from django.conf import settings

from user.models import Player


def read_recipients():
    """Read recipient data from recipients.csv file"""
    csv_file = Path(__file__).parent / 'export2.csv'
    if not csv_file.exists():
        raise FileNotFoundError(
            "recipients.csv file not found! Please create it with telegram_id and first_name columns.")

    recipients = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        csv_reader = csv.DictReader(f)
        # Verify required columns exist
        required_columns = {'telegram_id'}
        if not required_columns.issubset(csv_reader.fieldnames):
            missing = required_columns - set(csv_reader.fieldnames)
            raise ValueError(f"Missing required columns in CSV: {missing}")

        for row in csv_reader:
            recipients.append(row['telegram_id'].strip())
    return recipients


async def get_players():
    recipients = read_recipients()
    return list(await sync_to_async(
        lambda: list(Player.objects.all().exclude(telegram_id__in=recipients)),
        thread_sensitive=True
    )())


async def broadcast_message():
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    players = await get_players()

    if not players:
        print("No recipients found in recipients.csv file!")
        return

    for player in players:
        try:
            message = f"""<b>Hey {player.first_name}</b>, 👀🎲

The <b>top 100 players</b> just claimed their <b>Dice Passport NFT!</b> 🚀 But the game isn’t over yet…

Some NFTs are still <b>up for grabs</b>—and <b>you can claim them!</b>

Keep playing, stay on the <b>leaderboard</b>, and you might be next. 

<b>Will you make the cut?</b> 💰🔥


<a href='https://getgems.io/collection/EQAHvaW_p0tBOPI9Z74k6UgyLbox-FitPx1ixbRln7ZFyOrZ#activity'>Dicemaniacs Passport</a>
#DiceManiacs #DicePassport #UPD"""
            await bot.send_message(chat_id=player.telegram_id, text=message, parse_mode="HTML")
            # await bot.send_photo(chat_id=recipient['telegram_id'], photo="./data/media/5904615795118425431.jpg",
            #                    caption=message)
        except Exception as e:
            print(f"Failed to send message to {player.first_name} (ID: {player.telegram_id}): {e}")


def main():
    asyncio.run(broadcast_message())


if __name__ == '__main__':
    main()
