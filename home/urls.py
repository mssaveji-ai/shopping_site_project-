from django.urls import path
from . import views

urlpatterns = [
    path('',views.home_page.as_view(), name='home-page'),
    path('home-page-api/',views.Home_APIView.as_view(), name='home-page-api'),   
]
