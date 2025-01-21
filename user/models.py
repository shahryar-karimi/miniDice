from django.contrib.auth.models import AbstractUser
from django.db import models
from django_autoutils.model_utils import AbstractModel


class Player(AbstractModel):
    telegram_id = models.BigIntegerField(unique=True, primary_key=True)
    telegram_username = models.CharField(max_length=255, null=True)
    telegram_language_code = models.CharField(max_length=16, default='en')
    auth_token = models.CharField(max_length=255, null=True, blank=True)
    wallet_address = models.CharField(max_length=255, null=True)

    USERNAME_FIELD = 'telegram_id'
    USERNAME_FIELDS = ['telegram_username']

    def __str__(self):
        return self.telegram_username

    class Meta:
        db_table = 'player'
        verbose_name = 'Player'
        verbose_name_plural = 'Players'


class Prediction(AbstractModel):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    dice_number1 = models.IntegerField()
    dice_number2 = models.IntegerField()

    class Meta:
        db_table = 'prediction'
        verbose_name = 'Prediction'
        verbose_name_plural = 'Predictions'
