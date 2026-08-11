from django.db import models
from accounts.models import User
from products.models import Products

class Order(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='orders')
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateTimeField(blank=True,null=True)

    def calculate_total_price(self):
        total_price = 0
        for item in self.order_details.all():
            if self.is_paid:
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
