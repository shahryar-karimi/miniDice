from django.urls import path
from .views import *

urlpatterns = [
    path('auth/', TelegramAuthView.as_view(), name='auth'),
]
