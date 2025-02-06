from django.urls import path
from .views import *

urlpatterns = [
    path('predict/', PredictDiceAPI.as_view(), name='predict'),
    path('count-down/', CountDownResultAPI.as_view(), name='countDown'),
    path('end-event/', EndCountDownResultAPI.as_view(), name='end-event'),
    path('winners/', LastWinnersAPI.as_view(), name='winners'),
    path('connect-wallet/', ConnectWalletAPI.as_view(), name='connect-wallet'),
    path('player/', PlayerInfoAPI.as_view(), name='end-event'),
    path('referral-code/', ReferralCodeAPI.as_view(), name='referral-code'),
    path('referrals/', ReferralsAPI.as_view(), name='referrals'),
]
