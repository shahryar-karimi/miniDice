from django.contrib import admin
from django.contrib.admin import DateFieldListFilter
from django.db.models import F, Count, IntegerField, Case, When, Value
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin

from user.models import CountDown, Slot
from user.resource import *


class ConnectWalletFilter(admin.SimpleListFilter):
    title = _('wallet connected')  # Display name in the filter section
    parameter_name = 'wallet_address'  # URL query parameter

    def lookups(self, request, model_admin):
        return [
            ('none', _('Not Connected')),
            ('exist', _('Connected Wallet'))
        ]

    def queryset(self, request, queryset):
        if self.value() == 'none':
            return queryset.filter(wallet_address__isnull=True)
        if self.value() == 'exist':
            return queryset.filter(wallet_address__isnull=False)
        return queryset  # Default: show all


class OpenWebAppFilter(admin.SimpleListFilter):
    title = _('web app opened')  # Display name in the filter section
    parameter_name = 'auth_token'  # URL query parameter

    def lookups(self, request, model_admin):
        return [
            ('none', _('Not Opened')),
            ('exist', _('Opened Web App'))
        ]

    def queryset(self, request, queryset):
        if self.value() == 'none':
            return queryset.filter(auth_token__isnull=True)
        if self.value() == 'exist':
            return queryset.filter(auth_token__isnull=False)
        return queryset  # Default: show all


@admin.register(Player)
class PlayerAdmin(ImportExportModelAdmin):
    resource_class = PlayerResource
    list_display = (
        "telegram_id", "insert_dt", "telegram_username", "first_name", "last_name", "telegram_language_code",
        "auth_token", "referral_code", "available_slots", "wallet_address", "wallet_insert_dt", "point")
    search_fields = ("telegram_id", "telegram_username")
    list_filter = ("is_active", ConnectWalletFilter, OpenWebAppFilter, "telegram_language_code")
    fieldsets = (
        (None,
         {'fields': (
             "telegram_id", "referral_code", "telegram_username", "telegram_language_code", "auth_token",
             "wallet_address", "wallet_insert_dt")},),
    )
    ordering = ('telegram_id',)
    date_hierarchy = 'wallet_insert_dt'
    actions = ['sync_referrals']

    def point(self, obj):
        return obj.point

    point.admin_order_field = 'point_value'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            wallet=Case(
                When(wallet_address__isnull=False, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            ),
            win=Count('predictions', filter=F('predictions__is_win'), distinct=True),
            prediction=Count('predictions', distinct=True),
            referral_count=Count('refers', distinct=True),
            mini_app=Case(
                When(auth_token__isnull=False, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            )
        ).annotate(
            point_value=(
                    5 +
                    (10 * F('mini_app')) +
                    (500 * F('wallet')) +
                    (50 * F('win')) +
                    F('prediction') +
                    (5 * F('referral_count'))
            )
        )
        return queryset

    def sync_referrals(self, request, queryset):
        today = timezone.make_aware(timezone.datetime.combine(timezone.datetime.today(), timezone.datetime.min.time()))
        referrals = (Referral.objects.filter(insert_dt__gt=today)
                     .values('referrer')
                     .annotate(referral_count=Count('referrer')))
        for referrer_data in referrals:
            referrer_id = referrer_data['referrer']
            referral_count = referrer_data['referral_count']
            player = Player.objects.get(telegram_id=referrer_id)
            player.available_slots.number = referral_count + 1
            player.available_slots.save()


@admin.register(Slot)
class SlotAdmin(ImportExportModelAdmin):
    list_display = ["player", "countdown", "number"]
    list_filter = ["number", "countdown"]
    search_fields = ["player__telegram_id", "player__telegram_username"]


@admin.register(Prediction)
class PredictionAdmin(ImportExportModelAdmin):
    resource_class = PredictionResource
    list_display = (
        "player", "insert_dt", "countdown", "dice_number1", "dice_number2", "slot", "is_win", "is_active", "wallet",
        "amount")
    search_fields = ("player__telegram_username", "player__telegram_id")
    list_filter = ("dice_number1", "dice_number2", "slot", "is_win", "is_active", "countdown")
    fieldsets = (
        (None,
         {'fields': ("player", "dice_number1", "dice_number2", "countdown", "slot")},),
    )
    date_hierarchy = 'insert_dt'

    @admin.display(description='wallet address')
    def wallet(self, obj: Prediction):
        if obj.player.wallet_address:
            return obj.player.wallet_address
        return None

    @admin.display(description='amount')
    def amount(self, obj: Prediction):
        if obj.is_win:
            countdown = obj.countdown
            return countdown.amount / countdown.get_won_players_count()
        return 0


@admin.register(CountDown)
class CountDownAdmin(admin.ModelAdmin):
    list_display = (
        "insert_dt", "expire_dt", "dice_number1", "dice_number2", "is_active", "amount", "predictions_count",
        "won_players", "is_finished", "has_end")
    list_filter = ("is_active",)
    fieldsets = (
        (None,
         {'fields': ("expire_dt", "dice_number1", "dice_number2", "is_active", "amount", "has_end")},),
    )
    actions = ["end_countdown"]

    def end_countdown(self, request, queryset):
        countdowns = queryset.all()
        for countdown in countdowns:
            try:
                countdown.end_countdown()
                countdown.save()
            except Exception as e:
                pass

    @admin.display(description='Won players count')
    def won_players(self, obj: CountDown):
        if obj.is_finished:
            return obj.get_won_players_count()
        return 0

    @admin.display(description='All predictions count')
    def predictions_count(self, obj: CountDown):
        return obj.predictions.filter(is_active=True).count()


@admin.register(Referral)
class ReferralAdmin(ImportExportModelAdmin):
    resource_class = ReferralResource
    list_display = ("referrer", "referee", "insert_dt")
    fieldsets = (
        (None,
         {'fields': ("referrer", "referee")},),
    )
    search_fields = ['referrer__telegram_id', 'referrer__telegram_username', 'referrer__first_name',
                     'referrer__last_name']
    list_filter = [('insert_dt', DateFieldListFilter)]
    date_hierarchy = 'insert_dt'
