from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user'

    # def ready(self):
    #     # Ensure superuser creation on startup
    #     try:
    #         call_command('createsuperuser_if_none_exists')
    #     except Exception as e:
    #         pass
