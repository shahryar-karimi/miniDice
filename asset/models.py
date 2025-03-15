from decimal import Decimal

from django.db import models
from django_autoutils.model_utils import AbstractModel

from user.models import Player


class Asset(AbstractModel):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    master_address = models.CharField(max_length=255, null=True, blank=True)
    symbol = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    balance = models.DecimalField(max_digits=32, decimal_places=2, null=True, blank=True)
    decimal = models.IntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=56, decimal_places=24, null=True, blank=True)
    usd_value = models.DecimalField(max_digits=56, decimal_places=24, null=True, blank=True)

    def set_usd_value(self):
        if self.price:
            self.usd_value = (self.balance / 10 ** Decimal(self.decimal)) * self.price
        else:
            self.usd_value = 0

    def save(self, *args, force_insert=False, force_update=False, using=None, update_fields=None):
        if update_fields:
            self.set_usd_value()
            update_fields.append("usd_value")
        return super().save(*args, force_insert=force_insert, force_update=force_update, using=using,
                            update_fields=update_fields)

    class Meta:
        db_table = 'assets'
        verbose_name = 'Asset'
        verbose_name_plural = 'Assets'
