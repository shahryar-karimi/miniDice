import sys
from functools import wraps

import telegram
from asgiref.sync import sync_to_async

from user.models import Player, Referral

ERROR_MESSAGE = ('Oops! It seems that an error has occurred, please write to support (contact in bio)!')


@sync_to_async
def refer_player(referral_code, player):
    try:
        referrer = Player.objects.get(referral_code=referral_code)
        referrer.available_slots.add_slot()
        player.set_referral_code()
        Referral.objects.create(referrer=referrer, referee=player)
    except Referral.DoesNotExist:
        print("Referral does not exist")


def handler_decor(log_type='F', update_user_info=True):
    """

    :param log_type: 'F' -- функция, 'C' -- callback or command, 'U' -- user-status, 'N' -- NO LOG
    :param update_user_info: update user info if it has been changed
    :return:
    """

    def decor(func):
        @wraps(func)
        async def wrapper(update, context):
            def check_first_income():
                if update and update.message and update.message.text:
                    query_words = update.message.text.split()

            bot = context.bot
            referral_code = None
            if context.args and len(context.args) > 0:
                referral_code = context.args[0]

            user_details = update.effective_user

            if user_details is None:
                raise ValueError(
                    f'handler_decor is made for communication with user, current update has not any user: {update}'
                )

            user_adding_info = {
                'telegram_id': '{}'.format(user_details.id),
                'telegram_language_code': user_details.language_code or 'en',
                'telegram_username': user_details.username[:64] if user_details.username else '',
                'first_name': user_details.first_name[:30] if user_details.first_name else '',
                'last_name': user_details.last_name[:60] if user_details.last_name else '',
            }

            player, created = await Player.objects.aget_or_create(
                telegram_id=user_details.id,
                defaults=user_adding_info
            )
            if created:
                check_first_income()
            elif update_user_info:
                fields_changed = False
                for key in ['telegram_username', 'first_name', 'last_name']:
                    if getattr(player, key) != user_adding_info[key]:
                        setattr(player, key, user_adding_info[key])
                        fields_changed = True
                if fields_changed:
                    player.save()

            if not player.is_active:
                check_first_income()
                player.is_active = True
                await player.asave()
            if referral_code and created:
                await refer_player(referral_code, player)
            raise_error = None
            try:
                res = await func(bot, update, player)
            except telegram.error.BadRequest as error:
                if 'Message is not modified:' in error.message:
                    res = None
                else:
                    res = await bot.send_message(player.telegram_id,
                                                 str(ERROR_MESSAGE))  # should be bot.send_format_message
                    tb = sys.exc_info()[2]
                    raise_error = error.with_traceback(tb)
            except Exception as error:
                res = await bot.send_message(player.telegram_id,
                                             str(ERROR_MESSAGE))  # should be bot.send_format_message
                tb = sys.exc_info()[2]
                raise_error = error.with_traceback(tb)
            if log_type != 'N':
                if log_type == 'C':
                    if update.callback_query:
                        log_value = update.callback_query.data
                    else:
                        log_value = update.message.text
                elif log_type == 'U':
                    log_value = player.current_utrl
                else:
                    log_value = func.__name__

            if raise_error:
                raise raise_error

            return res

        return wrapper

    return decor
