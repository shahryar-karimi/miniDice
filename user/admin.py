from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from user.models import Player, Prediction, CountDown


# Register your models here.
class NullExistFilter(admin.SimpleListFilter):
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


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("telegram_id", "telegram_username", "telegram_language_code", "auth_token", "wallet_address")
    search_fields = ("telegram_id", "telegram_username")
    list_filter = ("is_active", NullExistFilter)
    fieldsets = (
        (None,
         {'fields': ("telegram_id", "telegram_username", "telegram_language_code", "auth_token", "wallet_address")},),
    )
    ordering = ('telegram_id',)


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = (
        "player", "insert_dt", "countdown", "dice_number1", "dice_number2", "is_win", "is_active", "wallet", "amount")
    search_fields = ("player__telegram_username", "player__telegram_id")
    list_filter = ("dice_number1", "dice_number2", "is_win", "is_active", "countdown")
    fieldsets = (
        (None,
         {'fields': ("player", "dice_number1", "dice_number2", "countdown")},),
    )

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
