from django.urls import path, include

from rest_framework import routers
from djoser.views import TokenCreateView, TokenDestroyView



router = routers.DefaultRouter()


urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/token/login/', TokenCreateView.as_view(), name='token_obtain'),
    path('auth/token/logout/', TokenDestroyView.as_view(), name='token_destroy')
]