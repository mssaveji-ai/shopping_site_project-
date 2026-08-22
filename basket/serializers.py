from rest_framework import serializers
from .models import OrderDetail, Order

class OrderDetailSerializer(serializers.ModelSerializer):
    item_total = serializers.SerializerMethodField()
    class Meta:
        model = OrderDetail
        fields = ['product', 'count','final_price','item_total']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.product:
            data['product'] = {
                'title': instance.product.title,
                'image': instance.product.image.url if instance.product.image else None,
                'price': instance.product.discount_price or instance.product.main_price,
            }

        else:
            data['product'] = None
        
        if not instance.order.is_paid:
            data['final_price'] = None
        
        return data
    
    def get_item_total(self, obj): 
        if obj.order.is_paid and obj.final_price is not None:
            return obj.final_price * obj.count
        
        if obj.product:
            current_price = obj.product.discount_price or obj.product.main_price
            return current_price * obj.count
        
        return 0

class OrderSerializer(serializers.ModelSerializer):
    order_details = OrderDetailSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id','user','is_paid','payment_date','order_details','total_price']
    
    def get_total_price(self, obj):
        return obj.calculate_total_price()