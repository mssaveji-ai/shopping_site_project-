from django.urls import path
from . import views

urlpatterns = [
    path('',views.Home_APIView.as_view(), name='home-page'),   
]
