from django.urls import path
from . import views

urlpatterns = [
    path('basket/',views.user_basket, name='basket-page'),
    path('api/basket/',views.UserBasketAPI.as_view(), name='api-basket-page'),
    path('add-to-order/',views.add_product_to_order, name='add-product-to-order'),
    path('api/add-to-order/',views.AddProductToOrderAPI.as_view(), name='api-add-product-to-order'),
    path('api/remove-from-order/<int:product_id>/',views.RemoveProductFromBasketAPI.as_view(), name='api-remove-product-from-order'),
    path('api/update-order/',views.UpdateProductCountAPI.as_view(), name='api-update-order'),
    path('api/checkout/',views.CheckOutAPI.as_view(), name='api-checkout'),
    path('api/payment-request/',views.PaymentRequestAPI.as_view(), name='payment-request'),
    path('api/payment-verify/',views.PaymentVerifyAPI.as_view(), name='payment-verify'),
    path('api/user-orders/',views.UserOrdersAPI.as_view(), name='user-ordersAPI'),
    path('api/order/<int:pk>/',views.OrderAPIView.as_view(), name='order-APIView'),

]