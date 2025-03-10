from django.db import models
from django_autoutils.model_utils import AbstractModel

from user.models import Player


class Asset(AbstractModel):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=255, null=True, blank=True)
    balance = models.DecimalField(max_digits=32, decimal_places=2, null=True, blank=True)
    decimal = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        db_table = 'assets'
        verbose_name = 'Asset'
        verbose_name_plural = 'Assets'

#
# class Token(AbstractModel):
#     token_symbol = models.CharField(max_length=255)
#     token_friendly_address = models.CharField(max_length=255, null=True)
#     price = models.DecimalField(max_digits=32, decimal_places=24, null=True)
#
#     class Meta:
#         db_table = 'tokens'
#         verbose_name = 'Token'
#         verbose_name_plural = 'Tokens'
#
#
#