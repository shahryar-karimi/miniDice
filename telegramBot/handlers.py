import telegram
from django.conf import settings
from telegram import (
    # TelegramObject,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram import Update, WebAppInfo

from user.models import User
from .utils import handler_decor


@handler_decor()
async def start(bot: telegram.Bot, update: Update, user: User):
    buttons = [
        [InlineKeyboardButton(
            text='Open Dice Maniacs',
            web_app=WebAppInfo(url=settings.FRONTEND_URL)
        )]
    ]

    msg = (
        "Hi this is a magic world for playing with dices and saving them from hostage.\n"
        "Press the button below to explore the Dice world!"
    )
    return await bot.send_message(
        chat_id=user.telegram_id,
        text=msg,
        reply_markup=InlineKeyboardMarkup(buttons)
    )