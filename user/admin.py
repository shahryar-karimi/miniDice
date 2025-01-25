from django.contrib import admin

from user.models import Player, Prediction, CountDown


# Register your models here.
@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("telegram_id", "telegram_username", "telegram_language_code", "auth_token", "wallet_address")
    search_fields = ("telegram_id", "telegram_username")
    list_filter = ("is_active",)
    fieldsets = (
        (None,
         {'fields': ("telegram_id", "telegram_username", "telegram_language_code", "auth_token", "wallet_address")},),
    )
    ordering = ('telegram_id',)


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ("player", "countdown", "dice_number1", "dice_number2", "is_win", "is_active")
    search_fields = ("dice_number1", "dice_number2")
    list_filter = ("dice_number1", "dice_number2", "is_win", "is_active", "countdown")
    fieldsets = (
        (None,
         {'fields': ("player", "dice_number1", "dice_number2", "countdown")},),
    )


@admin.register(CountDown)
class CountDownResultAdmin(admin.ModelAdmin):
    list_display = ("insert_dt", "expire_dt", "dice_number1", "dice_number2", "is_active", "amount")
    list_filter = ("is_active",)
    fieldsets = (
        (None,
         {'fields': ("expire_dt", "dice_number1", "dice_number2", "is_active", "amount")},),
    )
