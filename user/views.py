from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from user.serializers import *


class PredictDiceAPI(APIView):
    @swagger_auto_schema(
        operation_summary="Predict dice",
        operation_description="Simulates selecting two dice between 1 and 6 and saves it for users.",
        request_body=PredictDiceSerializer,
        responses={200: openapi.Response(
            description="Result predicted dice",
            examples={
                "application/json": {
                    "dice1": 3,
                    "dice2": 5
                }
            }
        )},
        tags=["Predict"]
    )
    def post(self, request):
        countdown = CountDown.get_active_countdown()
        if countdown.is_finished:
            return Response({"error": "Countdown is finished. wait for new event."}, status=status.HTTP_200_OK)
        player: Player = request.user
        predicted_dices = PredictDiceSerializer(data=request.data)
        predicted_dices.is_valid(raise_exception=True)
        predicted_dices.validated_data["player"] = player
        try:
            predicted_dices.is_valid_predict(player=player, countdown=countdown)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_200_OK)
        predicted_dices.save()
        return Response(predicted_dices.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Predict dice",
        operation_description="Simulates selecting two dice between 1 to 6 and saves it for users.",
        responses={200: openapi.Response(
            description="Result of last predicted dice",
            examples={
                "application/json": {
                    "predictions": [
                        {
                            "slot": 1,
                            "dice_number1": 3,
                            "dice_number2": 5
                        },
                        {
                            "slot": 1,
                            "dice_number1": 3,
                            "dice_number2": 5
                        },
                    ],
                    "slots": 2
                }
            }
        )},
        tags=["Predict"]
    )
    def get(self, request):
        count_down: "CountDown" = CountDown.get_active_countdown()
        if count_down.is_finished:
            return Response({"predictions": [], "slots": 1},
                            status=status.HTTP_200_OK)
        player: "Player" = request.user
        prediction = player.predictions.filter(is_active=True, countdown=count_down)
        serializer = PredictBoxSerializer({"predictions": prediction, "slots": player.predict_slot})
        return Response(serializer.data, status=status.HTTP_200_OK)


class CountDownResultAPI(APIView):
    @swagger_auto_schema(
        operation_summary="Count down expiration date",
        operation_description="Get count down expiration date with result of the 2 dices.",
        responses={200: openapi.Response(
            description="Count down",
            examples={
                "application/json": {
                    "expire_dt": "2025-01-21 15:44:42.210841+03:30",
                    "is_active": True
                }
            }
        )},
        tags=["Count down"]
    )
    def get(self, request):
        count_down: "CountDown" = CountDown.get_active_countdown()
        if count_down:
            serializer = CountDownTimeSerializer(count_down)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Active count down not found"}, status=status.HTTP_404_NOT_FOUND)


class EndCountDownResultAPI(APIView):
    @swagger_auto_schema(
        operation_summary="End countdown",
        operation_description="This api will run end process of countdown.",
        responses={200: openapi.Response(
            description="Count down",
            examples={
                "application/json": {
                    "expire_dt": "2025-01-21 15:44:42.210841+03:30",
                    "dice_number1": 6,
                    "dice_number2": 6
                }
            }
        )},
        tags=["Count down"]
    )
    def get(self, request):
        count_down: "CountDown" = CountDown.get_active_countdown()
        if count_down:
            try:
                count_down.end_countdown()
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            serializer = CountDownSerializer(data={"expire_dt": count_down.expire_dt,
                                                   "dice_number1": count_down.dice_number1,
                                                   "dice_number2": count_down.dice_number2})
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Active count down is not found"}, status=status.HTTP_404_NOT_FOUND)


class LastWinnersAPI(APIView):
    @swagger_auto_schema(
        operation_summary="Last winners",
        operation_description="Get last count down winners.",
        responses={200: openapi.Response(
            description="Count down",
            examples={
                "application/json": {
                    "predictions": [{
                        "username": "hamidmk",
                        "dice_number1": 6,
                        "dice_number2": 6,
                        "amount": 100
                    }, ]
                }
            }
        )},
        tags=["Count down"]
    )
    def get(self, request):
        countdown: "CountDown" = CountDown.objects.filter(expire_dt__lte=timezone.now()).order_by("-expire_dt").first()
        predictions = countdown.predictions.filter(is_win=True).distinct("player")
        serializer = PredictDiceSerializer(predictions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ConnectWalletAPI(APIView):
    @swagger_auto_schema(
        operation_summary="Connect wallet",
        operation_description="Get wallet address and saves it for player.",
        request_body=WalletAddressSerializer,
        tags=["Player"]
    )
    def post(self, request):
        serializer = WalletAddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            address = serializer.validated_data["wallet_address"]
        except Exception as e:
            return Response({"error": "Invalid data input"}, status=status.HTTP_400_BAD_REQUEST)
        player = request.user
        player.wallet_address = address
        if not player.wallet_insert_dt:
            player.wallet_insert_dt = timezone.now()
        player.save()
        return Response({"wallet_address": player.wallet_address}, status=status.HTTP_200_OK)


class PlayerInfoAPI(APIView):
    @swagger_auto_schema(
        operation_summary="Players base information",
        operation_description="Get player info",
        responses={200: openapi.Response(
            description="Count down",
            examples={
                "application/json": {
                    "telegram_id": 107290290,
                    "telegram_username": "shahryarkarimi",
                    "telegram_language_code": "en",
                    "wallet_address": "0x91203981203912830192380"
                }
            }
        )},
        tags=["Player"]
    )
    def get(self, request):
        player = request.user
        serializer = PlayerSerializer(player)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReferralCodeAPI(APIView):
    @swagger_auto_schema(
        operation_summary="Players referral code",
        operation_description="Get player referral code",
        responses={200: openapi.Response(
            description="Referral Code",
            examples={
                "application/json": {
                    "referral_code": 1023456789
                }
            }
        )},
        tags=["Player"]
    )
    def get(self, request):
        player = request.user
        player.set_referral_code()
        return Response({"referral_link": f"https://t.me/mini_dice_dev_bot?start={player.referral_code}"},
                        status=status.HTTP_200_OK)


class ReferralsAPI(APIView):
    @swagger_auto_schema(
        operation_summary="Players referrals",
        operation_description="Get player referrals",
        responses={200: openapi.Response(
            description="Referrals",
            examples={
                "application/json": {
                    "referrer": 1023456789
                }
            }
        )},
        tags=["Player"]
    )
    def get(self, request):
        player = request.user
        referrals = player.get_referrals()
        serializer = ReferralsListSerializer({"referral": referrals})
        return Response(serializer.data, status=status.HTTP_200_OK)


class MissionsCheckboxAPI(APIView):
    @swagger_auto_schema(
        operation_summary="Players referrals",
        operation_description="Get player referrals",
        responses={200: openapi.Response(
            description="Referrals",
            examples={
                "application/json": {
                    "referrer": 1023456789
                }
            }
        )},
        tags=["Player"]
    )
    def get(self, request):
        player = request.user
        if not player or not isinstance(player, Player):
            return Response({"error": "Authentication error."}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = MissionCheckboxSerializer(player)
        return Response(serializer.data, status=status.HTTP_200_OK)
