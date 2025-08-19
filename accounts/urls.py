from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/',views.Register.as_view(), name='register-form'),
    path('api/register/',views.RegisterAPI.as_view(), name='register-api-form'),
    path('account-activate/<str:activation_code>/',views.ActivateAccount.as_view(), name='activate_account'),
    path('api/account-activate/<str:activation_code>/',views.ActivateAccountAPI.as_view(), name='activate_api_account'),
    path('login/',views.Login.as_view(), name='login-form'),
    path('api/login/',views.LoginAPI.as_view(), name='login-api-form'),
    path('logout/',views.Logout.as_view(), name='logout-form'),
    path('api/logout/',views.LogoutAPI.as_view(), name='logout-api-form'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
