from django.shortcuts import render
from .models import Order
from django.http import JsonResponse
from .models import OrderDetail
from products.models import Products
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from.serializers import OrderSerializer
from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404

class UserBasketAPI(APIView):
    
    def get(self,request):
        new_order, created = Order.objects.prefetch_related('order_details').get_or_create(is_paid=False, user_id=request.user.id)
        srz_data = OrderSerializer(new_order).data
        return Response(srz_data)
        
def user_basket(request):
    new_order, created = Order.objects.prefetch_related('order_details').get_or_create(is_paid=False, user_id=request.user.id)
    sum = new_order.calculate_total_price()
    return render(request,'basket/basket.html',{'new_order':new_order,'sum':sum})


class AddProductToOrderAPI(APIView):
    
    def post(self, request):
        product_id = request.data.get('product_id')
        try:
            count = int(request.data.get('count'))
        except (TypeError, ValueError):
            return  Response({
                    'status':'invalid count',
                    'text':'The count must be number',
                    }, status=status.HTTP_400_BAD_REQUEST)

        if not product_id or not count:
            return  Response({
                    'status':'invalid data',
                    'icon':'error',
                    'confirmButtonText': 'Okay',
                    'text':'The product_id and count are required',
                    }, status=status.HTTP_400_BAD_REQUEST)
        if count<1:
            return  Response({
                    'status':'invalid count',
                    'icon':'error',
                    'confirmButtonText': 'Okay',
                    'text':'The quantity must be at least one',
                    }, status=status.HTTP_400_BAD_REQUEST)
        
        product = Products.objects.filter(id=product_id, is_delete=False).first()
        if product:
            new_order, created = Order.objects.get_or_create(is_paid=False, user_id=request.user.id)
            new_order_detail = new_order.order_details.filter(product_id=product_id).first()
            if new_order_detail:
                total_count = new_order_detail.count + count
                if product.stock < total_count:
                    return Response({
                    'status':'not enough stock',
                    'icon':'error',
                    'confirmButtonText': 'Okay',
                    'text':'The is not enough stock for this item',
                    }, status=status.HTTP_400_BAD_REQUEST)
                new_order_detail.count = total_count
                new_order_detail.save()
            else: 
               if product.stock < count:
                    return Response({
                        'status':'not enough stock',
                        'icon':'error',
                        'confirmButtonText': 'Okay',
                        'text':'The is not enough stock for this item',
                        }, status=status.HTTP_400_BAD_REQUEST)
           
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
    try:
        count = int(request.GET.get('count'))
    except (TypeError, ValueError):
        return JsonResponse({
            'status': 'invalid count',
            'text': 'The count must be number',
    }, status=400)

    if count<1:
        return  JsonResponse({
                'status':'invalid count',
                'icon':'error',
                'confirmButtonText': 'Okay',
                'text':'The quantity must be at least one',
                },  status=400)
    
    if request.user.is_authenticated:
        product = Products.objects.filter(id=product_id, is_delete=False).first()
        if product:
           new_order, created = Order.objects.get_or_create(is_paid=False, user_id=request.user.id)
           new_order_detail = new_order.order_details.filter(product_id=product_id).first()

           if new_order_detail:
                total_count = new_order_detail.count + count
                if product.stock < total_count:
                    return JsonResponse({
                    'status':'not enough stock',
                    'icon':'error',
                    'confirmButtonText': 'Okay',
                    'text':'The is not enough stock for this item',
                    })
                new_order_detail.count += count
                new_order_detail.save()
           else: 
               if product.stock < count:
                    return JsonResponse({
                        'status':'not enough stock',
                        'icon':'error',
                        'confirmButtonText': 'Okay',
                        'text':'The is not enough stock for this item',
                        })
           
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


class RemoveProductFromBasketAPI(APIView):
    def delete(self, request, product_id):
        order_detail = OrderDetail.objects.filter(order__user=request.user, order__is_paid=False, product__id=product_id).first()
        if not order_detail:
            return Response({
                "status":"Not Found",
                "Text": "Product is not found in your basket"
            }, status=status.HTTP_404_NOT_FOUND)
        
        order_detail.delete()
        return Response({
                "status":"success",
                "Text": "Product removed from your basket"
            }, status=status.HTTP_200_OK)

class UpdateProductCountAPI(APIView):


    def patch(self, request):
        product_id = request.data.get('product_id')

        try:
            count = int(request.data.get('count'))
        except (TypeError, ValueError):
            return Response(
                {"status": "Invalid count"},
                status=status.HTTP_400_BAD_REQUEST
             )

        if count < 1:
            return Response({
                "status":"Invalid count",
                "Text": "Count must be at least 1"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        order = Order.objects.filter(user=request.user, is_paid=False).first()
        if not order:
            return Response({
                "status":"Not found",
                "Text": "Basket not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        order_detail = OrderDetail.objects.filter(order=order, product_id=product_id).first()
        if not order_detail:
            return Response({
                "status":"Not found",
                "Text": "Product not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        if order_detail.product.stock < count:
                    return Response({
                    'status':'not enough stock',
                    'icon':'error',
                    'confirmButtonText': 'Okay',
                    'text':'The is not enough stock for this item',
                    }, status=status.HTTP_400_BAD_REQUEST)

        order_detail.count = count
        order_detail.save()
        return Response({
                "status":"success",
                "Text": "Product count updated"
            }, status=status.HTTP_200_OK)
    

class CheckOutAPI(APIView):
    def post(self, request):
        order = Order.objects.prefetch_related('order_details__product').filter(user=request.user, is_paid=False).first()
        if not order:
            return Response({
                "detail":"There is no active order for you."
            }, status=status.HTTP_404_NOT_FOUND)
        
        if not order.order_details.exists():
            return Response({
                "status":"Your basket is empty",
            }, status=status.HTTP_400_BAD_REQUEST)

        for item in order.order_details.all():
            if item.product is None:
                return Response({
                "status":"This item is no longer exists",
            }, status=status.HTTP_400_BAD_REQUEST)

            if item.product.stock < item.count:
                    return Response({
                "status":f"{item.product.title} is out of stock",
            }, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            for item in order.order_details.all():
                item.product.stock -= item.count
                item.product.save()
                item.final_price = item.product.discount_price or item.product.main_price
                item.save()

            order.is_paid = True
            order.payment_date = timezone.now()
            order.save()      

        return Response({
                "status":"Order has been paid successfully",
                "order_id": order.id
            }, status=status.HTTP_200_OK)


class UserOrdersAPI(APIView):
    def get(self, request):
        orders = Order.objects.prefetch_related('order_details__product').filter(user=request.user, is_paid=True)
        serializer = OrderSerializer(orders, many=True)

        return Response(serializer.data)
    
class OrderAPIView(APIView):

    def get(self, request, pk):
        order = get_object_or_404(Order.objects.prefetch_related("order_details"), user=request.user,id=pk, is_paid = True)
        serializer = OrderSerializer(order)

        return Response (serializer.data)