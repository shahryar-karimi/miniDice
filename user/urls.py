from django.urls import path
from .views import *

urlpatterns = [
    path('predict/', PredictDiceAPI.as_view(), name='predict'),
    path('predictions/', PredictionsAPI.as_view(), name='predictions'),
    path('count-down/', CountDownResultAPI.as_view(), name='countDown'),
    path('count-downs/', CountdownsAPI.as_view(), name='count-downs'),
    path('end-event/', EndCountDownResultAPI.as_view(), name='end-event'),
    path('winners/', LastWinnersAPI.as_view(), name='winners'),
    path('winners-by-countdown/', WinnersAPI.as_view(), name='winners-by-countdown'),
    path('connect-wallet/', ConnectWalletAPI.as_view(), name='connect-wallet'),
    path('player/', PlayerInfoAPI.as_view(), name='end-event'),
    path('referral-code/', ReferralCodeAPI.as_view(), name='referral-code'),
    path('referrals/', ReferralsAPI.as_view(), name='referrals'),
    path('missions/', MissionsCheckboxAPI.as_view(), name='missions'),
    path('leaderboard/', LeaderboardAPI.as_view(), name='leaderboard'),
]
