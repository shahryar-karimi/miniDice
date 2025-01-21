from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django_autoutils.model_utils import AbstractModel


class Player(AbstractModel):
    telegram_id = models.BigIntegerField(unique=True, primary_key=True)
    telegram_username = models.CharField(max_length=255, null=True)
    telegram_language_code = models.CharField(max_length=16, default='en')
    auth_token = models.CharField(max_length=255, null=True, blank=True)
    wallet_address = models.CharField(max_length=255, null=True)

    USERNAME_FIELD = 'telegram_id'
    USERNAME_FIELDS = ['telegram_id', 'telegram_username']

    def __str__(self):
        return self.telegram_username

    class Meta:
        db_table = 'player'
        verbose_name = 'Player'
        verbose_name_plural = 'Players'


class Prediction(AbstractModel):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    dice_number1 = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)])
    dice_number2 = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)])
    is_win = models.BooleanField(default=False)

    class Meta:
        db_table = 'prediction'
        verbose_name = 'Prediction'
        verbose_name_plural = 'Predictions'


class CountDownResult(AbstractModel):
    expire_dt = models.DateTimeField()
    dice_number1 = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)],
                                                    null=True,
                                                    blank=True)
    dice_number2 = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)],
                                                    null=True,
                                                    blank=True)

    def __str__(self):
        return f"{self.dice_number1} {self.dice_number2}"

    class Meta:
        db_table = 'countdown_result'
        verbose_name = 'CountDownResult'
        verbose_name_plural = 'CountDownResults'


