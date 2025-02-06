import datetime

from autoutils.script import id_generator
from constance import config
from django.utils import timezone


def token_generator():
    """
        Generate a token by configurable size
    """
    return id_generator(size=config.USER_TOKEN_SIZE)


def token_expire_dt_generator():
    """
        Generate expire datetime for token
    """
    return timezone.now() + datetime.timedelta(days=config.USER_TOKEN_EXPIRE_DAY)
