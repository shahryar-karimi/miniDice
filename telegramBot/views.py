import hashlib
import hmac
import time

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from miniDice import settings
from user.models import Player


class TelegramAuthView(APIView):
    @swagger_auto_schema(
        operation_summary="Authenticate for players",
        operation_description="Take telegram data to authenticate players and returns player_id",
        responses={200: openapi.Response(
            description="Count down",
            examples={
                "application/json": {
                    "player_id": 123456789,
                    "message": "Player authenticated successfully"
                }
            }
        )},
        tags=["count down"]
    )
    def post(self, request):
        # Extract Telegram data
        data = request.data
        telegram_data = data.get("telegram_data")
        if not telegram_data:
            return Response({"error": "Telegram data missing"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate Telegram data
        auth_date = int(telegram_data.get("auth_date"))
        if time.time() - auth_date > 86400:
            return Response({"error": "Auth date expired"}, status=status.HTTP_401_UNAUTHORIZED)

        secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
        check_hash = telegram_data.pop("hash")
        data_check_string = "\n".join([f"{k}={v}" for k, v in sorted(telegram_data.items())])
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        if calculated_hash != check_hash:
            return Response({"error": "Invalid data"}, status=status.HTTP_401_UNAUTHORIZED)

        # Get or create user
        player, created = Player.objects.get_or_create(
            telegram_id=telegram_data.get("id"),
            first_name=telegram_data.get("first_name"),
            last_name=telegram_data.get("last_name"),
            telegram_username=telegram_data.get("username"),
        )
        return Response({"player_id": player.telegram_id, "message": "Player authenticated successfully"})
