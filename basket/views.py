from django.shortcuts import render
from .models import Order
from django.http import JsonResponse
from .models import OrderDetail
from products.models import Products
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from.serializers import OrderSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication

class UserBasketAPI(APIView):
    permission_classes = [IsAuthenticated,]
    
    def get(self,request):
        new_order, created = Order.objects.prefetch_related('order_details').get_or_create(is_paid=False, user_id=request.user.id)
        srz_data = OrderSerializer(new_order).data
        return Response(srz_data)
        
def user_basket(request):
    new_order, created = Order.objects.prefetch_related('order_details').get_or_create(is_paid=False, user_id=request.user.id)
    sum = new_order.calculate_total_price
    return render(request,'basket/basket.html',{'new_order':new_order,'sum':sum})


class AddProductToOrderAPI(APIView):
    
    def post(self, request):
        product_id = request.data.get('product_id')
        count = int(request.data.get('count'))

        if count<1:
            return  Response({
                    'status':'invalid count',
                    'icon':'error',
                    'confirmButtonText': 'Okay',
                    'text':'The quantity must be at least one',
                    }, status=status.HTTP_400_BAD_REQUEST)
        
        product = Products.objects.filter(id=product_id).first()
        if product:
           new_order, created = Order.objects.prefetch_related('order_details').get_or_create(is_paid=False, user_id=request.user.id)
           new_order_detail = new_order.order_details.filter(product_id=product_id).first()
           if new_order_detail:
               new_order_detail.count += count
               new_order_detail.save()
           else:
               new_detail = OrderDetail(order_id=new_order.id,product_id=product_id,count=count)
               new_detail.save()
           return Response({
                'status':'success',
                'icon':'success',
                'confirmButtonText': 'Okay',
                'text':'The product has been added to your cart',
                },status=status.HTTP_200_OK )
        else:
            return Response({
                'status':'not found',
                'icon':'error',
                'confirmButtonText': 'Okay',
                'text':'The requested product was not found',
                }, status=status.HTTP_404_NOT_FOUND)
        
def add_product_to_order(request):
    product_id = request.GET.get('product_id')
    count = int(request.GET.get('count'))

    if count<1:
        return  JsonResponse({
                'status':'invalid count',
                'icon':'error',
                'confirmButtonText': 'Okay',
                'text':'The quantity must be at least one',
                })
    
    if request.user.is_authenticated:
        product = Products.objects.filter(id=product_id).first()
        if product:
           new_order, created = Order.objects.prefetch_related('order_details').get_or_create(is_paid=False, user_id=request.user.id)
           new_order_detail = new_order.order_details.filter(product_id=product_id).first()
           if new_order_detail:
               new_order_detail.count += count
               new_order_detail.save()
           else:
               new_detail = OrderDetail(order_id=new_order.id,product_id=product_id,count=count)
               new_detail.save()
           return JsonResponse({
                'status':'success',
                'icon':'success',
                'confirmButtonText': 'Okay',
                'text':'The product has been added to your cart',
                })
        else:
            return JsonResponse({
                'status':'not found',
                'icon':'error',
                'confirmButtonText': 'Okay',
                'text':'The requested product was not found',
                })
    else:
        return  JsonResponse({
                'status':'not log in',
                'icon':'error',
                'confirmButtonText': 'Okay',
                'text':'You need to log in before purchasing this product',
                }) 

