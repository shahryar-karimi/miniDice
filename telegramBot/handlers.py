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
            text='🎲 Predict Now 🎲',
            web_app=WebAppInfo(url=settings.FRONTEND_URL)
        )]
    ]

    msg = (
"""🎲 Welcome to Dice Maniacs! 🎲

Join the thrill and win your share of $100 every day with our daily airdrop! 💸

How to Participate:

1- Click on “🎲predict” to open mini app🤖
2- Connect Your Wallet 🔗
3- Join the Dice Maniacs Channel 📢
4- Guess the Correct Dice Combo 🎯
5- Check the @dicemaniacs channel at the Scheduled Time ⏰

✅ Guess correctly to claim your share of the $100 daily prize!

For more information, type /help.

Let the dice roll in your favor! 🎲💰"""
    )
    return await bot.send_message(
        chat_id=user.telegram_id,
        text=msg,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@handler_decor()
async def help(bot: telegram.Bot, update: Update, user: Player):
    msg = (
"""🎲 Frequently Asked Questions (FAQ)

What is the Dice Mini-App?
The Dice Mini-App 🎮 is your gateway to daily entertainment and rewards! Predict the results of live dice rolls 🐾 and compete for cash prizes 💸. It's transparent, thrilling, and easy to use!

How does it work?
• Login to the mini-app 🔑.
• Pick your prediction for the dice rolls (e.g., 3️⃣ & 5️⃣ or doubles like 4️⃣ & 4️⃣).
• Watch the dice roll live at 12 AM 🕛 nightly to see if you win!

When is the deadline to submit my prediction?
Submit your prediction anytime between 12:00 AM to 11:59 PM GMT 🕐.

What happens if my prediction is correct?
You’ll win a share of the $100 prize pool 💵, split equally among all correct predictions!

Is participation free?
Yes! Participation in all dice activities is completely free 🆓.

How can I watch the live dice roll?
Join us on our Telegram channel 📱 every night at 12:00 AM to watch the dice roll live 🎥.

How do I claim my prize?
Use the Connect Wallet 🔗 option in the mini-app. Prizes are credited to your wallet within 24 hours ⏳. Winners are also announced on the Telegram channel 🎉.

Can I change my prediction after submitting it?
Absolutely! You can revise your prediction as often as you like before 12:00 AM 🔄. Your most recent prediction will be final.

Can I submit multiple predictions in one day?
No. Each user is allowed one prediction per day ❌.

Is the competition fair?
100%! The dice rolls are conducted live for full transparency ⚖️, ensuring everyone has an equal chance to win.


How can I contact support?
Reach out to us via our @Dicemaniacs_Support for any questions or concerns.

Do I need to download anything to use the mini-app?
Nope! No installations required 🚫. Just access the mini-app from your preferred device and start playing instantly 📲.

🎲💰 Join the fun now and roll your way to exciting rewards! 💵✨"""
    )
    return await bot.send_message(
        chat_id=user.telegram_id,
        text=msg,
    )