from telegram.ext import (
    CommandHandler,
    Application,
)

from .handlers import start


def add_handlers(updater: Application):
    updater.add_handler(CommandHandler('start', start))