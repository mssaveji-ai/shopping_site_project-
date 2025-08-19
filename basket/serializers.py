from rest_framework import serializers
from .models import OrderDetail, Order

class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetail
        fields = ['product', 'count','final_price']

class OrderSerializer(serializers.ModelSerializer):
    order_details = OrderDetailSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id','user','is_paid','payment_date','order_details','total_price']
    
    def get_total_price(self, obj):
        return obj.calculate_total_price()