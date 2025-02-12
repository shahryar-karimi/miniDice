import random
import string

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django_autoutils.model_utils import AbstractModel


class Player(AbstractModel):
    telegram_id = models.BigIntegerField(unique=True, primary_key=True)
    telegram_username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    telegram_language_code = models.CharField(max_length=16, default='en')
    auth_token = models.CharField(max_length=255, null=True, blank=True)
    wallet_address = models.CharField(max_length=255, null=True, blank=True)
    wallet_insert_dt = models.DateTimeField(blank=True, null=True)
    referral_code = models.CharField(max_length=255, unique=True, null=True, blank=True)
    predict_slot = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(21)], default=1)

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

    def add_predict_slot(self):
        if self.predict_slot < 21:
            self.predict_slot += 1

    def set_referral_code(self):
        if not self.referral_code:
            self.referral_code = f"{self.telegram_id}{Player.generate_referral_code()}"
            self.save(update_fields=['referral_code'])

    @staticmethod
    def generate_referral_code():
        return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

    def get_referrals(self):
        return Referral.objects.filter(referrer=self)


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
            Player.objects.all().update(predict_slot=1)
        else:
            raise ValueError("Count down time is not finished yet.")

    def save(self, *args, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.id is None:
            CountDown.objects.filter(is_active=True).update(is_active=False)
        super().save(force_insert, force_update, using, update_fields)

    def get_won_players_count(self):
        return self.predictions.filter(is_win=True).distinct("player").count()

    @staticmethod
    def get_active_countdown():
        return CountDown.objects.get(is_active=True)

    @staticmethod
    def get_last_countdown():
        return CountDown.objects.filter(expire_dt__lte=timezone.now()).order_by("-expire_dt").first()


class Prediction(AbstractModel):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='predictions')
    dice_number1 = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)])
    dice_number2 = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)])
    is_win = models.BooleanField(default=False)
    countdown = models.ForeignKey(CountDown, on_delete=models.CASCADE, related_name='predictions')
    slot = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(21)], default=1)

    def save(self, *args, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.countdown_id is None:
            self.countdown = CountDown.objects.get(is_active=True)
        Prediction.objects.filter(is_active=True, player=self.player, countdown=self.countdown, slot=self.slot).update(
            is_active=False)
        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        db_table = 'prediction'
        verbose_name = 'Prediction'
        verbose_name_plural = 'Predictions'


class Referral(AbstractModel):
    referrer = models.ForeignKey(Player, on_delete=models.CASCADE, unique=False)
    referee = models.OneToOneField(Player, related_name="referrals", null=True, blank=True, on_delete=models.SET_NULL,
                                   unique=False)

    def __str__(self):
        return f"{self.referrer} -> {self.referee}"
