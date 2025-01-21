from django.urls import path
from .views import *

urlpatterns = [
    path('predict/', PredictDiceAPI.as_view(), name='predict'),
    path('count_down/', CountDownResultAPI.as_view(), name='countDown'),

]
