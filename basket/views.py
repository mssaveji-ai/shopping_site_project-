from django.shortcuts import render
from .models import Order, OrderDetail, Payment
from django.http import JsonResponse
from products.models import Products
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from.serializers import OrderSerializer
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404
import requests
from shopping_site import settings
from datetime import timedelta
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

        if not product_id:
            return Response({
                "status": "Product ID is required"
            }, status=status.HTTP_400_BAD_REQUEST)

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
        
        product = order_detail.product
        if product is None or product.is_delete:
            return Response({
                "status": "Product is no longer available"
            }, status=status.HTTP_400_BAD_REQUEST)
        
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
        
        now = timezone.now()

        for item in order.order_details.all():
            product = item.product

            if product is None or product.is_delete:
                return Response({
                "status":f"This product is no longer exists",
            }, status=status.HTTP_400_BAD_REQUEST)

            reserved_count = (OrderDetail.objects.filter(product=product, order__is_paid=False, order__payment_expires_at__gt=now)
                            .exclude(order=order).aggregate(total=Sum('count'))['total'] or 0)
            available_stock = product.stock - reserved_count

            if item.count > available_stock:
                    return Response({
                "status":f"{product.title} is out of stock",
            }, status=status.HTTP_400_BAD_REQUEST)    

        return Response({
                "status":"Order is ready to payment",
                "order_id": order.id,
            }, status=status.HTTP_200_OK)

def reset_payment(payment):
        payment.authority = None
        payment.expires_at = None
        payment.status = "failed"
        payment.save()

        for order_detail in payment.order.order_details.all():
            order_detail.final_price = None
            order_detail.save()     
class PaymentRequestAPI(APIView):
    def post(self, request):
        now = timezone.now()
        
        with transaction.atomic():
                order = Order.objects.select_for_update().filter(user=request.user, is_paid=False).first()

                if not order:
                    return Response({
                        "status":"Order not found",
                    }, status=status.HTTP_404_NOT_FOUND)
                
                if not order.order_details.exists():
                    return Response(
                        {
                            "detail": "Your basket is empty."
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                payment = order.payments.order_by("-created_at").first()

                if (payment
                    and payment.expires_at
                    and payment.status == 'requested'
                    and payment.authority
                    and payment.expires_at > now):
                
                            payment_url = f"https://sandbox.zarinpal.com/pg/StartPay/{payment.authority}"
                            return Response({
                                    "order_id":order.id,
                                    'authority': payment.authority,
                                    "payment_url" : payment_url,
                                    "amount": payment.amount
                                })  
                
                if (payment
                    and payment.expires_at
                    and payment.expires_at <= now 
                    and payment.status in ['pending', 'requested']):
                    
                    payment.status = 'expired'
                    payment.expires_at = None
                    payment.save()
                    
                if (payment
                    and payment.status == 'pending'
                    and payment.expires_at
                    and payment.expires_at > now ):
                        return Response({
                                "status":"Payment request is already being proceed",
                            }, status=status.HTTP_409_CONFLICT) 

                total_price = 0
                for order_detail in order.order_details.select_related("product").all():
                    product = order_detail.product

                    if not product or product.is_delete:
                        return Response({
                            "detail":"This product no longer exists."
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    product = Products.objects.select_for_update().get(id=product.id)
                    
                    reserved_count = (OrderDetail.objects.filter(product=product, order__is_paid=False, order__payment_expires_at__gt=now)
                                    .exclude(order=order).aggregate(total=Sum('count'))['total'] or 0)
                    available_stock = product.stock - reserved_count

                    if order_detail.count > available_stock:

                            return Response({
                                "status":f"{product.title} is out of stock",
                            }, status=status.HTTP_400_BAD_REQUEST)   

                    final_price = (product.discount_price or product.main_price)

                    order_detail.final_price = final_price
                    order_detail.save()

                    total_price += (final_price * order_detail.count)

                payment = Payment.objects.create(order=order, status='pending', amount=total_price, expires_at= now + timedelta(minutes=10))
                
        data = {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "amount": payment.amount,
            "callback_url": "http://127.0.0.1:8000/api/payment-verify/",
            "description": f"Payment for order {order.id}"
        } 

        try:
            response = requests.post(
                "https://sandbox.zarinpal.com/pg/v4/payment/request.json",
                json=data,
                timeout=15
            )
            result = response.json()


        except requests.RequestException:
                
            with transaction.atomic():
                order = Order.objects.select_for_update().get(id=order.id)
                payment = Payment.objects.select_for_update().get(id=payment.id)
                if not order.is_paid:
                    reset_payment(payment)

                return Response ({
                    'detail' : "Could not connect to payment gateway"
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        except ValueError:

            with transaction.atomic():
                order = Order.objects.select_for_update().get(id=order.id)
                payment = Payment.objects.select_for_update().get(id=payment.id)

                if not order.is_paid:
                    reset_payment(payment)

                return Response ({
                    'detail' : "Invalid Response from payment gateway"
                }, status=status.HTTP_502_BAD_GATEWAY)

        getaway_data = result.get('data',{})
        getaway_code = getaway_data.get('code')

        if getaway_code == 100:
            authority = getaway_data.get('authority')

            if not authority:
                with transaction.atomic():
                    order = Order.objects.select_for_update().get(id=order.id)
                    payment = Payment.objects.select_for_update().get(id=payment.id)
                    if payment.status != 'paid':
                        reset_payment(payment)
                    return Response({
                        "detail": "Payment authority was not returned",
                    }, status=status.HTTP_502_BAD_GATEWAY)
                
            with transaction.atomic():
                order = Order.objects.select_for_update().get(id=order.id)
                payment = Payment.objects.select_for_update().get(id=payment.id)

                if order.is_paid:
                    return Response({
                        "detail": "Order is already paid."
                    }, status=status.HTTP_409_CONFLICT)

                payment.authority = authority
                payment.status = "requested"
                payment.save()
                payment_url = f"https://sandbox.zarinpal.com/pg/StartPay/{authority}"

                return Response({
                    "order_id": order.id,
                    "payment_id": payment.id,
                    'authority': authority,
                    'payment_url':payment_url,
                    'amount': payment.amount
                })

        with transaction.atomic():
            order = Order.objects.select_for_update().get(id=order.id)
            payment = Payment.objects.select_for_update().get(id=payment.id)
            if payment.status != 'paid':
                reset_payment(payment)

        return Response(result, status=status.HTTP_400_BAD_REQUEST)

class PaymentVerifyAPI(APIView):
    permission_classes=[AllowAny]

    def get(self, request):
        authority = request.GET.get('Authority')
        status_value = request.GET.get('Status')
        
        if not authority:
            return Response({
                    "detail": "Payment authority is missing."
                },status=status.HTTP_400_BAD_REQUEST)

        if status_value != 'OK':

            with transaction.atomic():
                order = Order.objects.select_for_update().filter(payment_authority=authority, is_paid=False).first()
                if order:
                    reset_payment(order)

                return Response({
                        'status' : 'Payment failed'
                        }, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.prefetch_related('order_details__product').filter(payment_authority=authority).first()

        if not order:
            return Response({
                'status' : 'Order not found'
                }, status=status.HTTP_404_NOT_FOUND)
        
        if not order.payment_amount:
            return Response(
                {
                    "detail": "Payment amount is missing"
                }, status=status.HTTP_400_BAD_REQUEST)
        
        verify_data = {
            "merchant_id" : settings.ZARINPAL_MERCHANT_ID,
            'amount' : order.payment_amount,
            'authority' : order.payment_authority
        }

        try:
            response = requests.post("https://sandbox.zarinpal.com/pg/v4/payment/verify.json", json=verify_data, timeout=15)
            result = response.json()
        
        except requests.RequestException:
            with transaction.atomic():
                order = Order.objects.select_for_update().get(id=order.id)
                if not order.is_paid:
                    reset_payment(order)

            return Response({
                'detail': "Could not connect to payment geteway"
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        except ValueError:
            with transaction.atomic():
                order = Order.objects.select_for_update().get(id=order.id)
                if not order.is_paid:
                    reset_payment(order)

            return Response({
                'detail': "Invalid response from payment geteway"
            }, status=status.HTTP_502_BAD_GATEWAY)
        
        geteway_data = result.get('data',{})
        code = geteway_data.get('code')
        ref_id = geteway_data.get('ref_id')

        if code in [100,101]:
            with transaction.atomic():
                order = Order.objects.select_for_update().get(id=order.id)

                if order.is_paid:
                    return Response({
                        "status": "payment successfull",
                    }, status=status.HTTP_200_OK)

                products_list = []
                for order_detail in order.order_details.all():
                    
                    if not order_detail.product or order_detail.product.is_delete:
                        order.payment_status = "verified_stock_issue"
                        order.save()

                        return Response({
                            "detail": "This product is no longer exists",
                            "order_id": order.id,
                            "ref_id": geteway_data.get("ref_id")
                        },status=status.HTTP_409_CONFLICT)

                    product = Products.objects.select_for_update().get(id=order_detail.product_id)

                    if order_detail.count > product.stock:
                        order.payment_status = "verified_stock-issue"
                        order.save()

                        return Response({
                            'status' : f"{product.title} is no longer available in requested quantity",
                            'order_id': order.id,
                            'ref_id': result["data"].get('ref_id')
                            }, status=status.HTTP_409_CONFLICT)
                    
                    products_list.append((product, order_detail.count))

                for product, count in products_list:
                    product.stock -= count
                    product.save()

                order.is_paid = True
                order.payment_date = timezone.now()
                order.payment_expires_at = None
                order.payment_ref_id = ref_id
                order.payment_status = "paid"
                order.save()

                return Response({
                    'status' : 'Payment Successful',
                    "order_id" : order.id,
                    "ref_id" : result['data'].get("ref_id")
                    })
        with transaction.atomic():
            order = Order.objects.select_for_update().get(id=order.id)
            reset_payment(order)

        return Response(result, status=status.HTTP_400_BAD_REQUEST)

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