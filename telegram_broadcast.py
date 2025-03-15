import asyncio
import os
from pathlib import Path

import django
from telegram import Bot

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'miniDice.settings')
django.setup()
from django.conf import settings

def read_recipients():
    """Read recipient telegram IDs from recipients.txt file"""
    recipients_file = Path(__file__).parent / 'recipients.txt'
    if not recipients_file.exists():
        raise FileNotFoundError("recipients.txt file not found! Please create it with telegram IDs.")
    
    with open(recipients_file, 'r') as f:
        # Read lines and filter out comments and empty lines
        telegram_ids = [
            line.strip() for line in f
            if line.strip() and not line.strip().startswith('#')
        ]
    return telegram_ids

async def broadcast_message():
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    telegram_ids = read_recipients()
    
    if not telegram_ids:
        print("No recipients found in recipients.txt file!")
        return
        
    for telegram_id in telegram_ids:
        try:
            message = f"""🎉Hello, NEW Dice Maniacs Citizen! 🎲

You've joined through a recommendation, and we've got AMAZING things waiting for you in Dice Land! 🌍✨

🚨$20 Retention Bonus and $30 Referral Bonus are just the beginning! And don't forget about the $100 prize every night! 💰🔥

Connect your wallet to start your adventure and claim your rewards! 🔗🚀

Come back and join the fun—the experience is just starting! 🎉🎲"""
            await bot.send_photo(chat_id=telegram_id, photo="./data/media/5904615795118425431.jpg",
                               caption=message)
            print(f"Successfully sent message to {telegram_id}")
        except Exception as e:
            print(f"Failed to send message to {telegram_id}: {e}")

def main():
    asyncio.run(broadcast_message())

if __name__ == '__main__':
    main() 