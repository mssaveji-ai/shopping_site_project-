from django.db import models
from accounts.models import User
from products.models import Products

class Order(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='orders')
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateTimeField(blank=True,null=True)
    payment_authority = models.CharField(max_length=255, null=True, blank=True)
    payment_ref_id = models.CharField(max_length=255, null=True, blank=True)
    payment_amount = models.PositiveBigIntegerField(null=True, blank=True)
    payment_expires_at = models.DateTimeField(null=True, blank=True)
    payment_status = models.CharField(max_length=20, default="none")
    refund_status = models.CharField(max_length=20, default="none")
    refund_date = models.DateTimeField(null=True, blank=True)

    def calculate_total_price(self):
        total_price = 0
        for item in self.order_details.all():
            if self.is_paid and item.final_price is not None:
                total_price += item.final_price * item.count
            else:
                price = item.product.discount_price or item.product.main_price
                total_price += price * item.count
        return total_price

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user'], condition = models.Q(is_paid=False), name='unique_active_order_per_user')]

    def __str__(self):
        return f"{self.id}: Order of {self.user}"

class OrderDetail(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name='order_details')
    product = models.ForeignKey(Products,on_delete=models.SET_NULL,null=True, related_name='product_basket')
    final_price = models.IntegerField(null=True,blank=True)
    count = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.count} of {self.product} in {self.order} "


# Create your models here.

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='payments')
    authority = models.CharField(max_length=255, unique=True)
    ref_id = models.CharField(max_length=255, null=True, blank=True)
    amount = models.PositiveBigIntegerField()
    status = models.CharField(max_length=20, default="pending")
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payment {self.id} - order {self.order_id} "
    
