from django.urls import path
from . import views

urlpatterns = [
    path('basket/',views.user_basket,name='basket-page'),
    path('api/basket/',views.UserBasketAPI.as_view(),name='api-basket-page'),
    path('add-to-order/',views.add_product_to_order,name='add-product-to-order'),
    path('api/add-to-order/',views.AddProductToOrderAPI.as_view(),name='api-add-product-to-order'),
]