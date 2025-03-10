from django.contrib import admin
from django.contrib.admin import DateFieldListFilter
from django.db.models import Count, Prefetch, Q
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
        "auth_token", "referral_code", "available_slots", "wallet_address", "wallet_insert_dt", "point_value")
    search_fields = ("telegram_id", "telegram_username")
    list_filter = ("is_active", ConnectWalletFilter, OpenWebAppFilter, "telegram_language_code")
    fieldsets = (
        (None,
         {'fields': (
             "telegram_id", "referral_code", "telegram_username", "first_name", "last_name", "telegram_language_code",
             "auth_token", "wallet_address", "wallet_insert_dt")},),
    )
    ordering = ('telegram_id',)
    date_hierarchy = 'wallet_insert_dt'
    actions = ['sync_referrals']

    def point_value(self, obj):
        return obj.point_value

    point_value.admin_order_field = 'point_value'

    def available_slots(self, obj):
        if hasattr(obj, 'available_slot') and obj.available_slot:
            slot = obj.available_slot[0]
            return slot.number
        return "No active slot"

    available_slots.admin_order_field = 'available_slots'

    def get_queryset(self, request):
        active_countdown = CountDown.get_active_countdown()
        queryset = super().get_queryset(request).prefetch_related(
            Prefetch('slot_set', queryset=Slot.objects.filter(countdown=active_countdown), to_attr='available_slot'))
        return Player.players_with_point_value(queryset)

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
        "id", "insert_dt", "expire_dt", "dice_number1", "dice_number2", "is_active", "amount", "predictions_count",
        "won_players", "is_finished", "has_end")
    list_filter = ("is_active",)
    fieldsets = (
        (None,
         {'fields': ("expire_dt", "dice_number1", "dice_number2", "is_active", "amount", "has_end")},),
    )
    actions = ["end_countdown"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request).annotate(
            predictions_count=Count('predictions', filter=Q(predictions__is_active=True)),
            won_players=Count('predictions', filter=Q(predictions__is_win=True)))
        return queryset

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
        if hasattr(obj, 'won_players') and obj.won_players:
            return obj.won_players
        return 0

    @admin.display(description='All predictions count')
    def predictions_count(self, obj: CountDown):
        if hasattr(obj, 'predictions_count') and obj.predictions_count:
            return obj.predictions_count
        return 0


@admin.register(Referral)
class ReferralAdmin(ImportExportModelAdmin):
    resource_class = ReferralResource
    list_display = ("referrer", "referee", "insert_dt", "referee_wallet")
    fieldsets = (
        (None,
         {'fields': ("referrer", "referee")},),
    )
    search_fields = ['referrer__telegram_id', 'referrer__telegram_username', 'referrer__first_name',
                     'referrer__last_name']
    list_filter = [('insert_dt', DateFieldListFilter)]
    date_hierarchy = 'insert_dt'

    @admin.display(description='referee wallet')
    def referee_wallet(self, obj: Referral):
        return obj.referee.wallet_address
