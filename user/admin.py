from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin
from django.contrib.admin import DateFieldListFilter
from user.models import Player, Prediction, CountDown, Referral
from user.resource import PlayerResource, PredictionResource


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
class PlayerAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = PlayerResource
    list_display = (
        "telegram_id", "insert_dt", "telegram_username", "first_name", "last_name", "telegram_language_code",
        "auth_token", "referral_code", "predict_slot", "wallet_address", "wallet_insert_dt")
    search_fields = ("telegram_id", "telegram_username")
    list_filter = ("is_active", ConnectWalletFilter, OpenWebAppFilter)
    fieldsets = (
        (None,
         {'fields': (
             "telegram_id", "referral_code", "telegram_username", "telegram_language_code", "auth_token",
             "wallet_address", "predict_slot", "wallet_insert_dt")},),
    )
    ordering = ('telegram_id',)
    date_hierarchy = 'wallet_insert_dt'


@admin.register(Prediction)
class PredictionAdmin(ImportExportModelAdmin, admin.ModelAdmin):
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
        "insert_dt", "expire_dt", "dice_number1", "dice_number2", "is_active", "amount", "won_players", "is_finished")
    list_filter = ("is_active",)
    fieldsets = (
        (None,
         {'fields': ("expire_dt", "dice_number1", "dice_number2", "is_active", "amount")},),
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


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ("referrer", "referee", "insert_dt")
    fieldsets = (
        (None,
         {'fields': ("referrer", "referee")},),
    )
    search_fields = ['referrer__telegram_id', 'referrer__telegram_username', 'referrer__first_name',
                     'referrer__last_name']
    list_filter = [('insert_dt', DateFieldListFilter)]
    date_hierarchy = 'insert_dt'
