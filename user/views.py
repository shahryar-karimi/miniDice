from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from user.models import Player
from user.models import Prediction
from user.serializers import PredictDiceSerializer


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
    )
    def post(self, request):
        user = request.user
        predicted_dices = PredictDiceSerializer(data=request.data)
        print(request.data)
        predicted_dices.is_valid(raise_exception=True)
        predicted_dices.validated_data["player"] = user
        predicted_dices.save()
        return Response(predicted_dices.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Predict dice",
        operation_description="Simulates selecting two dice between 1 to 6 and saves it for users.",
        responses={200: openapi.Response(
            description="Result of last predicted dice",
            examples={
                "application/json": {
                    "dice_number1": 3,
                    "dice_number2": 5
                }
            }
        )},
    )
    def get(self, request):
        player: "Player" = request.user
        print(player.__str__())
        prediction = Prediction.objects.filter(player=player, is_active=True).order_by("-insert_dt").first()
        return Response({"dice_number1": prediction.dice_number1, "dice_number2": prediction.dice_number2},
                        status=status.HTTP_200_OK)

