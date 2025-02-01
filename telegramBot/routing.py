from telegram.ext import (
    CommandHandler,
    Application,
)

from .handlers import start, help


def add_handlers(updater: Application):
    updater.add_handler(CommandHandler('start', start))
    updater.add_handler(CommandHandler('help', help))

