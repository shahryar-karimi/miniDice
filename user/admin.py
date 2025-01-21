from django.contrib import admin

from user.models import Player, Prediction, CountDownResult


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
    list_display = ("player", "dice_number1", "dice_number2", "is_win", "is_active")
    search_fields = ("dice_number1", "dice_number2")
    list_filter = ("dice_number1", "dice_number2", "is_win", "is_active")
    fieldsets = (
        (None,
         {'fields': ("player", "dice_number1", "dice_number2")},),
    )


@admin.register(CountDownResult)
class CountDownResultAdmin(admin.ModelAdmin):
    list_display = ("insert_dt", "expire_dt", "dice_number1", "dice_number2", "is_active")
    list_filter = ("is_active",)
    fieldsets = (
        (None,
         {'fields': ("expire_dt", "dice_number1", "dice_number2", "is_active")},),
    )
