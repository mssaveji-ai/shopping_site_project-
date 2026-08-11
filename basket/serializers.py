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
        
        return data
    
    def get_item_total(self, obj): 
        return obj.final_price * obj.count

class OrderSerializer(serializers.ModelSerializer):
    order_details = OrderDetailSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id','user','is_paid','payment_date','order_details','total_price']
    
    def get_total_price(self, obj):
        return obj.calculate_total_price()