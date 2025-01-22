import telegram
from django.conf import settings
from telegram import (
    # TelegramObject,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram import Update, WebAppInfo

from user.models import Player
from .utils import handler_decor


@handler_decor()
async def start(bot: telegram.Bot, update: Update, user: Player):
    buttons = [
        [InlineKeyboardButton(
            text='Open Dice Predictor',
            web_app=WebAppInfo(url=settings.FRONTEND_URL)
        )]
    ]

    msg = (
        "Hi this is a magic world for predicting two dices and earning money.\n"
        "Press the button below to guess the correct dices!"
    )
    return await bot.send_message(
        chat_id=user.telegram_id,
        text=msg,
        reply_markup=InlineKeyboardMarkup(buttons)
    )