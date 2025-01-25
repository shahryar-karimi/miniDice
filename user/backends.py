from typing import Optional

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User

from user.models import Player


class TokenAuthenticationBackend(BaseBackend):
    """
        use this model for handle extra data of user
    """

    def authenticate(self, request, username=None, password=None, token=None, **kwargs):
        try:
            user = User.objects.get(username=username, password=password)
            return user
        except User.DoesNotExist:
            pass
        try:
            player = Player.objects.get(wallet_address=token)
            return player
        except Player.DoesNotExist:
            pass
        return None

    def get_user(self, user_id) -> "Optional[User]":
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
