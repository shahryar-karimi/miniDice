from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

from user.models import Player


class UserTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, token):
        if not token:
            raise exceptions.AuthenticationFailed(_("token not found"))
        try:
            player = Player.objects.get(auth_token=token)
        except Player.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('invalid token.'))
        if not player.is_active:
            raise exceptions.AuthenticationFailed(_('player inactive or deleted.'))
        return player, token
