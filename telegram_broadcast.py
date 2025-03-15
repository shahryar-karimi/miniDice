import asyncio
import os
from pathlib import Path
import csv

import django
from telegram import Bot

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'miniDice.settings')
django.setup()
from django.conf import settings

def read_recipients():
    """Read recipient data from recipients.csv file"""
    csv_file = Path(__file__).parent / 'export2.csv'
    if not csv_file.exists():
        raise FileNotFoundError("recipients.csv file not found! Please create it with telegram_id and first_name columns.")
    
    recipients = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        csv_reader = csv.DictReader(f)
        # Verify required columns exist
        required_columns = {'Telegram ID', 'First Name'}
        if not required_columns.issubset(csv_reader.fieldnames):
            missing = required_columns - set(csv_reader.fieldnames)
            raise ValueError(f"Missing required columns in CSV: {missing}")
            
        for row in csv_reader:
            recipients.append({
                'telegram_id': row['Telegram ID'].strip(),
                'first_name': row['First Name'].strip()
            })
    return recipients

async def broadcast_message():
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    recipients = read_recipients()
    
    if not recipients:
        print("No recipients found in recipients.csv file!")
        return
        
    for recipient in recipients:
        try:
            message = f"""🎉 Hello {recipient['first_name']}, NEW Dice Maniacs Citizen! 🎲

You've joined through a recommendation, and we've got AMAZING things waiting for you in Dice Land! 🌍✨

🚨$20 Retention Bonus and $30 Referral Bonus are just the beginning! And don't forget about the $100 prize every night! 💰🔥

Connect your wallet to start your adventure and claim your rewards! 🔗🚀

Come back and join the fun—the experience is just starting! 🎉🎲"""
            await bot.send_photo(chat_id=recipient['telegram_id'], photo="./data/media/5904615795118425431.jpg",
                               caption=message)
            print(f"Successfully sent message to {recipient['first_name']} (ID: {recipient['telegram_id']})")
        except Exception as e:
            print(f"Failed to send message to {recipient['first_name']} (ID: {recipient['telegram_id']}): {e}")

def main():
    asyncio.run(broadcast_message())

if __name__ == '__main__':
    main() 