from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
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
        player = request.user
        if not player or not isinstance(player, Player):
            return Response({"error": "Authentication error."}, status=status.HTTP_401_UNAUTHORIZED)
        if not player.wallet_address:
            return Response({"error": "Wallet is not connected yet."}, status=status.HTTP_200_OK)
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
        player = request.user
        if not player or not isinstance(player, Player):
            return Response({"error": "Authentication error."}, status=status.HTTP_401_UNAUTHORIZED)
        _predictions = player.predictions.filter(is_active=True, countdown=count_down).order_by("slot")
        slots = player.available_slots.number
        predictions = list(_predictions)
        for i in range(1, slots + 1):
            if not _predictions.filter(slot=i).exists():
                predictions.append({"slot": i, "dice_number1": None, "dice_number2": None})
        serializer = PredictBoxSerializer({"predictions": predictions, "slots": slots})
        return Response(serializer.data, status=status.HTTP_200_OK)


class CountDownResultAPI(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

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
        prev_count_down: "CountDown" = CountDown.get_last_countdown()
        if prev_count_down:
            try:
                prev_count_down.end_countdown()
                prev_count_down.save()
            except Exception:
                pass
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
        count_down: "CountDown" = CountDown.get_last_countdown()
        if count_down:
            try:
                count_down.end_countdown()
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            serializer = CountDownSerializer(count_down)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Active count down is not found"}, status=status.HTTP_404_NOT_FOUND)


class LastWinnersAPI(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

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
        countdown: "CountDown" = CountDown.get_last_countdown()
        predictions = countdown.predictions.filter(is_win=True).distinct("player")
        serializer = PredictDiceSerializer(predictions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WinnersAPI(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="winners",
        operation_description="Get winners by count down.",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description="This is countdown id",
                              type=openapi.TYPE_INTEGER, required=True),
        ],
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
        countdown_id = request.query_params.get('id')
        if not CountDown.objects.filter(id=countdown_id).exists():
            return Response({"error": "Count down not found."}, status=status.HTTP_404_NOT_FOUND)
        countdown: "CountDown" = CountDown.objects.get(pk=countdown_id)
        if not countdown.is_finished:
            return Response({"error": "Countdown is not finished yet."}, status=status.HTTP_400_BAD_REQUEST)
        predictions = countdown.predictions.filter(is_win=True)
        serializer = PredictDiceSerializer(predictions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CountdownsAPI(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Countdowns",
        operation_description="Get all count downs.",
        responses={200: openapi.Response(
            description="Count down",
            examples={
                "application/json": {
                    "predictions": [{
                        "id": 4,
                        "expire_dt": "2025-01-21 15:44:42.210841+03:30"
                    }, ]
                }
            }
        )},
        tags=["Count down"]
    )
    def get(self, request):
        countdowns = CountDown.objects.filter(expire_dt__lt=timezone.now()).order_by("-expire_dt")
        serializer = CountdownListSerializer(countdowns, many=True)
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
        is_first_time = False
        if Player.objects.filter(wallet_address=address).exists():
            is_first_time = True
        player = request.user
        if not player or not isinstance(player, Player):
            return Response({"error": "Authentication error."}, status=status.HTTP_401_UNAUTHORIZED)
        player.wallet_address = address
        if not player.wallet_insert_dt:
            player.wallet_insert_dt = timezone.now()
        player.save()
        return Response({"wallet_address": player.wallet_address, "is_first_time": is_first_time},
                        status=status.HTTP_200_OK)


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
        if not player or not isinstance(player, Player):
            return Response({"error": "Authentication error."}, status=status.HTTP_401_UNAUTHORIZED)
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
        if not player or not isinstance(player, Player):
            return Response({"error": "Authentication error."}, status=status.HTTP_401_UNAUTHORIZED)
        player.set_referral_code()
        return Response({"referral_link": f"https://t.me/Dicemaniacs_bot?start={player.referral_code}"},
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
        if not player or not isinstance(player, Player):
            return Response({"error": "Authentication error."}, status=status.HTTP_401_UNAUTHORIZED)
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


class PredictionsAPI(APIView):
    @swagger_auto_schema(
        operation_summary="Prediction history",
        operation_description="Gets all predictions of a player .",
        responses={status.HTTP_200_OK: PredictionHistoryRowSerializer(many=True)},
        tags=["Predict"]
    )
    def get(self, request):
        player = request.user
        if not player or not isinstance(player, Player):
            return Response({"error": "Authentication error."}, status=status.HTTP_401_UNAUTHORIZED)
        predictions = player.predictions.order_by("-insert_dt")
        serializer = PredictionHistoryRowSerializer(predictions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LeaderboardAPI(APIView):
    @swagger_auto_schema(
        operation_summary="Prediction history",
        operation_description="Gets all predictions of a player .",
        responses={status.HTTP_200_OK: LeaderboardSerializer()},
        tags=["Leaderboard"]
    )
    def get(self, request):
        serializer = LeaderboardSerializer(data={})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
