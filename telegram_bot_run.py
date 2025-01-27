from telegram.ext import ApplicationBuilder
from telegram import Bot, Update
import os, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'miniDice.settings')
django.setup()

from miniDice.settings import TELEGRAM_BOT_TOKEN
from telegramBot.routing import add_handlers


def main():
    print("Starting connection with bot")
    bot = Bot(TELEGRAM_BOT_TOKEN)
    print("Connected successfully!")
    application = ApplicationBuilder().bot(bot).build()
    add_handlers(application)
    print("Loading application")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    print("Application loaded successfully!")


if __name__ == '__main__':
    main()
