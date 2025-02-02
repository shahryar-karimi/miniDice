from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django_autoutils.model_utils import AbstractModel


class Player(AbstractModel):
    telegram_id = models.BigIntegerField(unique=True, primary_key=True)
    telegram_username = models.CharField(max_length=255, null=True)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    telegram_language_code = models.CharField(max_length=16, default='en')
    auth_token = models.CharField(max_length=255, null=True, blank=True)
    wallet_address = models.CharField(max_length=255, null=True, blank=True)

    USERNAME_FIELD = 'telegram_id'
    USERNAME_FIELDS = ['telegram_id', 'telegram_username']

    def __str__(self):
        if self.telegram_username:
            return self.telegram_username
        else:
            return str(self.telegram_id)

    class Meta:
        db_table = 'player'
        verbose_name = 'Player'
        verbose_name_plural = 'Players'

    def telegram_login(self):
        self.auth_token = self.telegram_id
        self.save()


class CountDown(AbstractModel):
    expire_dt = models.DateTimeField()
    dice_number1 = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)],
                                                    null=True,
                                                    blank=True)
    dice_number2 = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)],
                                                    null=True,
                                                    blank=True)
    amount = models.PositiveIntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return f"({self.dice_number1} {self.dice_number2}) {self.expire_dt}"

    class Meta:
        db_table = 'countdown_result'
        verbose_name = 'CountDownResult'
        verbose_name_plural = 'CountDownResults'

    @cached_property
    def is_finished(self):
        return self.expire_dt <= timezone.now()

    def end_countdown(self):
        predictions_filter = self.predictions.filter(is_active=True)
        predictions_filter.update(is_win=False)
        if self.is_finished:
            predictions_filter.filter(dice_number1=self.dice_number1, dice_number2=self.dice_number2).update(
                is_win=True)
            predictions_filter.filter(dice_number1=self.dice_number2, dice_number2=self.dice_number1).update(
                is_win=True)
        else:
            raise ValueError("Count down time is not finished yet.")

    def save(self, *args, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.id is None:
            CountDown.objects.filter(is_active=True).update(is_active=False)
        super().save(force_insert, force_update, using, update_fields)

    def get_won_players_count(self):
        return self.predictions.filter(is_win=True).count()


class Prediction(AbstractModel):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    dice_number1 = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)])
    dice_number2 = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)])
    is_win = models.BooleanField(default=False)
    countdown = models.ForeignKey(CountDown, on_delete=models.CASCADE, related_name='predictions')

    def save(self, *args, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.countdown_id is None:
            self.countdown = CountDown.objects.get(is_active=True)
        if not self.countdown.is_finished:
            Prediction.objects.filter(is_active=True, player=self.player, countdown=self.countdown).update(
                is_active=False)
        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        db_table = 'prediction'
        verbose_name = 'Prediction'
        verbose_name_plural = 'Predictions'
